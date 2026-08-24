import fs from "fs";
import path from "path";

export type AddressStyle = "formal" | "informal";
export type OnboardingStage = "awaiting_style" | "done";
export type Platform = "telegram" | "max" | "web";

export interface StoredMessage {
  role: "user" | "bot";
  text: string;
  timestamp: string;
  contextTag?: string;
}

export interface UserProfile {
  userId: string;
  platform: Platform;
  name: string;
  addressStyle: AddressStyle;
  onboardingStage: OnboardingStage;
  coreFacts: string[];
  recentSummary: string;
  messages: StoredMessage[];
  escalationStatus: "none" | "watching" | "escalated";
  createdAt: string;
  lastActiveAt: string;
  timezone?: string;
}

const MESSAGES_IN_PROMPT = 20;

export interface UserStorage {
  getUser(userId: string): Promise<UserProfile | null>;
  getAllUsers(): Promise<UserProfile[]>;
  createUser(userId: string, platform: Platform, name: string, timezone?: string): Promise<UserProfile>;
  updateUser(userId: string, patch: Partial<UserProfile>): Promise<UserProfile | null>;
  appendMessage(userId: string, role: "user" | "bot", text: string, contextTag?: string): Promise<void>;
}

function makeNewProfile(userId: string, platform: Platform, name: string, timezone: string): UserProfile {
  const now = new Date().toISOString();
  return {
    userId, platform, name,
    addressStyle: "formal",
    onboardingStage: "awaiting_style",
    coreFacts: [],
    recentSummary: "",
    messages: [],
    escalationStatus: "none",
    createdAt: now,
    lastActiveAt: now,
    timezone,
  };
}

class FileUserStorage implements UserStorage {
  private file: string;
  private cache: Record<string, UserProfile> | null = null;

  constructor(dataDir: string) {
    this.file = path.join(dataDir, "users.json");
    if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true });
  }
  private load(): Record<string, UserProfile> {
    if (this.cache) return this.cache;
    try {
      this.cache = fs.existsSync(this.file) ? JSON.parse(fs.readFileSync(this.file, "utf-8")) : {};
    } catch (err) {
      console.error("userStore(file): read error", err);
      this.cache = {};
    }
    return this.cache!;
  }
  private persist() {
    try {
      fs.writeFileSync(this.file, JSON.stringify(this.cache || {}, null, 2), "utf-8");
    } catch (err) {
      console.error("userStore(file): persist error", err);
    }
  }
  async getUser(userId: string) { return this.load()[userId] || null; }
  async getAllUsers() { return Object.values(this.load()); }
  async createUser(userId: string, platform: Platform, name: string, timezone = "Europe/Moscow") {
    const profile = makeNewProfile(userId, platform, name, timezone);
    this.load()[userId] = profile;
    this.persist();
    return profile;
  }
  async updateUser(userId: string, patch: Partial<UserProfile>) {
    const users = this.load();
    const existing = users[userId];
    if (!existing) return null;
    users[userId] = { ...existing, ...patch, lastActiveAt: new Date().toISOString() };
    this.persist();
    return users[userId];
  }
  async appendMessage(userId: string, role: "user" | "bot", text: string, contextTag?: string) {
    const users = this.load();
    const existing = users[userId];
    if (!existing) return;
    existing.messages.push({ role, text, timestamp: new Date().toISOString(), contextTag });
    existing.lastActiveAt = new Date().toISOString();
    this.persist();
  }
}

// Firestore storage (прод, персистентно). Требует USE_FIRESTORE=true.
class FirestoreUserStorage implements UserStorage {
  private col: any;
  constructor() {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const { Firestore } = require("@google-cloud/firestore");
    const collectionName = process.env.FIRESTORE_USERS_COLLECTION || "coach_users";
    const db = new Firestore({
      ignoreUndefinedProperties: true,
      databaseId: process.env.FIRESTORE_DATABASE_ID || "coach-db",
    });
    this.col = db.collection(collectionName);
    console.log(`[userStore] Firestore enabled (collection: ${collectionName})`);
  }
  async getUser(userId: string): Promise<UserProfile | null> {
    const doc = await this.col.doc(userId).get();
    return doc.exists ? (doc.data() as UserProfile) : null;
  }
  async getAllUsers(): Promise<UserProfile[]> {
    const snap = await this.col.get();
    return snap.docs.map((d: any) => d.data() as UserProfile);
  }
  async createUser(userId: string, platform: Platform, name: string, timezone = "Europe/Moscow"): Promise<UserProfile> {
    const profile = makeNewProfile(userId, platform, name, timezone);
    await this.col.doc(userId).set(profile);
    return profile;
  }
  async updateUser(userId: string, patch: Partial<UserProfile>): Promise<UserProfile | null> {
    const ref = this.col.doc(userId);
    const doc = await ref.get();
    if (!doc.exists) return null;
    const updated = { ...(doc.data() as UserProfile), ...patch, lastActiveAt: new Date().toISOString() };
    await ref.set(updated);
    return updated;
  }
  async appendMessage(userId: string, role: "user" | "bot", text: string, contextTag?: string): Promise<void> {
    const ref = this.col.doc(userId);
    const doc = await ref.get();
    if (!doc.exists) return;
    const profile = doc.data() as UserProfile;
    profile.messages.push({ role, text, timestamp: new Date().toISOString(), contextTag });
    profile.lastActiveAt = new Date().toISOString();
    await ref.set(profile);
    // Для высокой нагрузки лучше хранить сообщения в подколлекции
    // (users/{id}/messages) вместо массива в документе — лимит документа 1 МБ.
  }
}

function createUserStorage(dataDir: string): UserStorage {
  if (process.env.USE_FIRESTORE === "true") {
    try {
      return new FirestoreUserStorage();
    } catch (err) {
      console.error("[userStore] Firestore init failed, falling back to file storage:", err);
      return new FileUserStorage(dataDir);
    }
  }
  console.log("[userStore] Using file storage (data/users.json). Set USE_FIRESTORE=true for persistence.");
  return new FileUserStorage(dataDir);
}

const DATA_DIR = path.join(process.cwd(), "data");
const store = createUserStorage(DATA_DIR);

export async function getUser(userId: string): Promise<UserProfile | null> {
  return store.getUser(userId);
}
export async function getAllUsers(): Promise<UserProfile[]> {
  return store.getAllUsers();
}
export async function createUser(userId: string, platform: Platform, name: string, timezone = "Europe/Moscow"): Promise<UserProfile> {
  return store.createUser(userId, platform, name, timezone);
}
export async function updateUser(userId: string, patch: Partial<UserProfile>): Promise<UserProfile | null> {
  return store.updateUser(userId, patch);
}
export async function appendMessage(userId: string, role: "user" | "bot", text: string, contextTag?: string): Promise<void> {
  return store.appendMessage(userId, role, text, contextTag);
}
export function getRecentHistoryForPrompt(profile: UserProfile): string {
  const recent = profile.messages.slice(-MESSAGES_IN_PROMPT);
  return recent.map((m) => `${m.role === "user" ? profile.name : "Опрус (коуч)"}: ${m.text}`).join("\n");
}
export async function setEscalationStatus(userId: string, status: UserProfile["escalationStatus"]): Promise<void> {
  await updateUser(userId, { escalationStatus: status });
}

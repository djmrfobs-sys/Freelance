import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { X, FileText, Printer, ShieldCheck, Check, Phone, Mail, MapPin } from "lucide-react";

export interface Requisites {
  companyName: string;
  inn: string;
  ogrn: string;
  address: string;
  phone: string;
  email: string;
  website: string;
}

export const requisitesData: Requisites = {
  companyName: "Индивидуальный предприниматель Киселев Артур Пшимахович",
  inn: "231406735404",
  ogrn: "312231421500020",
  address: "352505, Краснодарский край, г. Лабинск, ул. Филатова, д. 45",
  phone: "8-928-432-12-76",
  email: "dj.mr.fobs@gmail.com",
  website: "https://t.me/kiselevy_creo"
};

export type DocumentType = "privacy" | "terms" | "personal_data" | "marketing";

interface LegalDocumentsModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialTab?: DocumentType;
}

export const LegalDocumentsModal: React.FC<LegalDocumentsModalProps> = ({
  isOpen,
  onClose,
  initialTab = "privacy"
}) => {
  const [activeTab, setActiveTab] = useState<DocumentType>(initialTab);

  const handlePrint = () => {
    window.print();
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-shanti-dark/70 backdrop-blur-xs overflow-y-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          className="relative w-full max-w-3xl bg-white rounded-3xl shadow-2xl overflow-hidden border border-shanti-earth my-4 flex flex-col max-h-[92vh]"
        >
          {/* Header */}
          <div className="p-5 sm:p-6 bg-shanti-light border-b border-shanti-earth flex items-center justify-between shrink-0">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-shanti-green/10 flex items-center justify-center text-shanti-green shrink-0">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-serif font-bold text-shanti-dark text-base sm:text-lg leading-tight">
                  Правовые документы и соглашения
                </h3>
                <p className="font-sans text-[11px] text-shanti-olive uppercase tracking-wider font-semibold">
                  ИП Киселев Артур Пшимахович
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handlePrint}
                className="p-2 text-shanti-olive hover:text-shanti-dark hover:bg-shanti-earth/30 rounded-full transition-colors cursor-pointer"
                title="Распечатать документ"
              >
                <Printer className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={onClose}
                className="p-2 text-shanti-olive hover:text-shanti-dark hover:bg-shanti-earth/30 rounded-full transition-colors cursor-pointer"
                title="Закрыть"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="bg-shanti-sand/60 p-2 border-b border-shanti-earth flex gap-1 overflow-x-auto shrink-0">
            <button
              type="button"
              onClick={() => setActiveTab("privacy")}
              className={`px-3 py-2 rounded-xl text-xs font-sans font-medium whitespace-nowrap transition-all cursor-pointer ${
                activeTab === "privacy"
                  ? "bg-shanti-green text-white font-bold shadow-xs"
                  : "text-gray-600 hover:text-shanti-dark hover:bg-white/60"
              }`}
            >
              1. Политика конфиденциальности
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("terms")}
              className={`px-3 py-2 rounded-xl text-xs font-sans font-medium whitespace-nowrap transition-all cursor-pointer ${
                activeTab === "terms"
                  ? "bg-shanti-green text-white font-bold shadow-xs"
                  : "text-gray-600 hover:text-shanti-dark hover:bg-white/60"
              }`}
            >
              2. Пользовательское соглашение
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("personal_data")}
              className={`px-3 py-2 rounded-xl text-xs font-sans font-medium whitespace-nowrap transition-all cursor-pointer ${
                activeTab === "personal_data"
                  ? "bg-shanti-green text-white font-bold shadow-xs"
                  : "text-gray-600 hover:text-shanti-dark hover:bg-white/60"
              }`}
            >
              3. Согласие на ОПД
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("marketing")}
              className={`px-3 py-2 rounded-xl text-xs font-sans font-medium whitespace-nowrap transition-all cursor-pointer ${
                activeTab === "marketing"
                  ? "bg-shanti-green text-white font-bold shadow-xs"
                  : "text-gray-600 hover:text-shanti-dark hover:bg-white/60"
              }`}
            >
              4. Согласие на рассылку
            </button>
          </div>

          {/* Document Content */}
          <div className="p-5 sm:p-8 overflow-y-auto space-y-6 text-shanti-dark text-xs sm:text-sm leading-relaxed font-sans select-text">
            {activeTab === "privacy" && (
              <div className="space-y-4">
                <div className="text-center pb-3 border-b border-shanti-earth">
                  <h2 className="font-serif font-bold text-base sm:text-lg text-shanti-dark uppercase tracking-tight">
                    ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ
                  </h2>
                  <p className="font-serif italic text-shanti-olive text-xs mt-1">
                    Индивидуального предпринимателя Киселева Артура Пшимаховича
                  </p>
                </div>

                <div className="space-y-3 text-justify">
                  <h3 className="font-bold font-serif text-sm text-shanti-dark">1. Общие положения</h3>
                  <p>Эта Политика определяет, как я обрабатываю и защищаю персональные данные пользователей моих сервисов, сайтов, ботов и приложений.</p>
                  <p>Используя мои сервисы, вы соглашаетесь с условиями этой Политики.</p>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">2. Какие данные собираются</h3>
                  <p><b>Вы добровольно предоставляете:</b></p>
                  <ul className="list-disc list-inside pl-2 space-y-1">
                    <li>имя или никнейм</li>
                    <li>номер телефона</li>
                    <li>адрес электронной почты</li>
                    <li>идентификатор аккаунта в мессенджере (Telegram ID)</li>
                    <li>другие данные, которые вы сами решаете передать</li>
                  </ul>
                  <p className="pt-1"><b>Автоматически собирается:</b></p>
                  <ul className="list-disc list-inside pl-2 space-y-1">
                    <li>IP-адрес</li>
                    <li>тип браузера или устройства</li>
                    <li>дата и время посещения</li>
                  </ul>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">3. Зачем собираются данные</h3>
                  <p>Я собираю данные для того, чтобы:</p>
                  <ul className="list-disc list-inside pl-2 space-y-1">
                    <li>предоставлять доступ к сервисам и работать с вами</li>
                    <li>общаться с вами (поддержка, уведомления)</li>
                    <li>отправлять информационные и рекламные рассылки (только с вашего согласия)</li>
                    <li>улучшать качество сервисов</li>
                    <li>соблюдать требования законодательства</li>
                  </ul>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">4. На каком основании я обрабатываю данные</h3>
                  <p>Я обрабатываю данные на основании:</p>
                  <ul className="list-disc list-inside pl-2 space-y-1">
                    <li>Федерального закона от 27.07.2006 N 152-ФЗ "О персональных данных"</li>
                    <li>Федерального закона от 13.03.2006 N 38-ФЗ "О рекламе"</li>
                    <li>вашего согласия</li>
                  </ul>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">5. Как я храню и защищаю данные</h3>
                  <p>Я храню данные на защищенных серверах с ограниченным доступом. Я принимаю все необходимые меры, чтобы защитить ваши данные от несанкционированного доступа, уничтожения, изменения или распространения.</p>
                  <p>Доступ к данным есть только у меня и уполномоченных лиц.</p>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">6. Передача данных третьим лицам</h3>
                  <p>Я не передаю ваши данные третьим лицам, за исключением случаев:</p>
                  <ul className="list-disc list-inside pl-2 space-y-1">
                    <li>когда это требует закон</li>
                    <li>когда это необходимо для работы сервиса (хостинг-провайдеры) — в минимальном объеме</li>
                    <li>когда вы сами дали на это согласие</li>
                  </ul>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">7. Сколько хранятся данные</h3>
                  <p>Данные хранятся, пока не будет достигнута цель их обработки, либо пока вы не отзовете свое согласие.</p>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">8. Ваши права</h3>
                  <p>Вы имеете право:</p>
                  <ul className="list-disc list-inside pl-2 space-y-1">
                    <li>узнать, какие данные о вас хранятся</li>
                    <li>попросить уточнить, заблокировать или удалить ваши данные</li>
                    <li>отозвать согласие на обработку данных</li>
                    <li>отписаться от рассылки (ссылка для отписки есть в каждом сообщении)</li>
                  </ul>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">9. Сторонние сервисы</h3>
                  <p>В работе могут использоваться сторонние сервисы: Supabase, Telegram Bot API, Lovable.dev, GitHub, Instagram Graph API, хостинг-провайдеры. Я не несу ответственность за обработку данных сторонними сервисами.</p>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">10. Контакты</h3>
                  <p>По всем вопросам, связанным с персональными данными, пишите:</p>
                  <p className="font-semibold text-shanti-dark">
                    Индивидуальный предприниматель Киселев Артур Пшимахович<br />
                    ИНН: {requisitesData.inn} | ОГРНИП: {requisitesData.ogrn}<br />
                    Адрес: {requisitesData.address}<br />
                    Телефон: {requisitesData.phone}<br />
                    Email: <a href={`mailto:${requisitesData.email}`} className="text-shanti-green underline">{requisitesData.email}</a>
                  </p>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">11. Изменение Политики</h3>
                  <p>Я могу менять эту Политику. Новая версия вступает в силу с момента публикации, если не указано иное.</p>
                </div>
              </div>
            )}

            {activeTab === "terms" && (
              <div className="space-y-4">
                <div className="text-center pb-3 border-b border-shanti-earth">
                  <h2 className="font-serif font-bold text-base sm:text-lg text-shanti-dark uppercase tracking-tight">
                    ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ
                  </h2>
                  <p className="font-serif italic text-shanti-olive text-xs mt-1">
                    Индивидуального предпринимателя Киселева Артура Пшимаховича
                  </p>
                </div>

                <div className="space-y-3 text-justify">
                  <h3 className="font-bold font-serif text-sm text-shanti-dark">1. Общие положения</h3>
                  <p>Это Соглашение регулирует отношения между мной, Индивидуальным предпринимателем Киселевым Артуром Пшимаховичем, и вами, пользователем моих сервисов, ботов, сайтов и приложений.</p>
                  <p>Используя мои сервисы, вы соглашаетесь с условиями этого Соглашения. Если вы не согласны — не используйте сервисы.</p>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">2. Что я предоставляю</h3>
                  <p>Я даю вам доступ к своим сервисам, включая:</p>
                  <ul className="list-disc list-inside pl-2 space-y-1">
                    <li>Telegram-боты и Telegram-каналы</li>
                    <li>веб-сайты и веб-приложения</li>
                    <li>сервисы автоматизации и AI-ассистенты</li>
                    <li>информационные и консультационные услуги</li>
                  </ul>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">3. Что вы обязаны делать</h3>
                  <p>Вы обязуетесь:</p>
                  <ul className="list-disc list-inside pl-2 space-y-1">
                    <li>использовать сервисы по назначению</li>
                    <li>не ломать и не взламывать сервисы</li>
                    <li>не передавать доступ к сервисам другим людям</li>
                    <li>соблюдать законы РФ</li>
                  </ul>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">4. Что я обязан делать</h3>
                  <p>Я обязуюсь: обеспечивать доступ к сервисам, не разглашать ваши данные (кроме случаев по закону), сообщать об изменениях в работе сервисов.</p>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">5. Интеллектуальная собственность</h3>
                  <p>Все права на сервисы (код, дизайн, контент) принадлежат мне. Вы не можете копировать, изменять или распространять мои сервисы без моего письменного согласия.</p>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">6. Платные услуги</h3>
                  <p>Некоторые сервисы могут быть платными. Цены указаны в сервисе. Возврат средств осуществляется согласно правилам законодательства РФ.</p>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">7. Ответственность</h3>
                  <p>Сервисы предоставляются "как есть". Я не гарантирую, что они будут работать без ошибок и перебоев. Моя максимальная ответственность ограничена суммой, которую вы заплатили за последние 12 месяцев.</p>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">8. Персональные данные</h3>
                  <p>Использование сервисов регулируется Политикой конфиденциальности и Согласием на обработку персональных данных.</p>

                  <h3 className="font-bold font-serif text-sm text-shanti-dark pt-2">9. Контакты</h3>
                  <p className="font-semibold text-shanti-dark">
                    ИП Киселев Артур Пшимахович<br />
                    ИНН: {requisitesData.inn} | ОГРНИП: {requisitesData.ogrn}<br />
                    Адрес: {requisitesData.address}<br />
                    Телефон: {requisitesData.phone}<br />
                    Email: {requisitesData.email}
                  </p>
                </div>
              </div>
            )}

            {activeTab === "personal_data" && (
              <div className="space-y-4">
                <div className="text-center pb-3 border-b border-shanti-earth">
                  <h2 className="font-serif font-bold text-base sm:text-lg text-shanti-dark uppercase tracking-tight">
                    СОГЛАСИЕ НА ОБРАБОТКУ ПЕРСОНАЛЬНЫХ ДАННЫХ
                  </h2>
                  <p className="font-serif italic text-shanti-olive text-xs mt-1">
                    ИП Киселеву Артуру Пшимаховичу (ФЗ № 152-ФЗ)
                  </p>
                </div>

                <div className="space-y-3 text-justify">
                  <p>
                    Я, являясь пользователем сервисов, сайтов, ботов и приложений Индивидуального предпринимателя Киселева Артура Пшимаховича, свободно и в своем интересе даю согласие на обработку своих персональных данных.
                  </p>
                  <p className="p-3 bg-shanti-sand/80 rounded-xl border border-shanti-earth font-mono text-xs">
                    <b>Кто обрабатывает:</b> Индивидуальный предприниматель Киселев Артур Пшимахович<br />
                    <b>ИНН:</b> {requisitesData.inn} | <b>ОГРНИП:</b> {requisitesData.ogrn}<br />
                    <b>Адрес:</b> {requisitesData.address}
                  </p>

                  <p className="font-bold pt-1">Какие данные обрабатываются:</p>
                  <ul className="list-disc list-inside pl-2 space-y-1">
                    <li>фамилия, имя, отчество (если указано)</li>
                    <li>номер телефона</li>
                    <li>адрес электронной почты</li>
                    <li>идентификатор в мессенджере или соцсети (Telegram ID, Instagram ID)</li>
                    <li>другие данные, которые я добровольно предоставляю</li>
                  </ul>

                  <p className="font-bold pt-1">Зачем обрабатываются данные:</p>
                  <ul className="list-disc list-inside pl-2 space-y-1">
                    <li>чтобы я мог пользоваться сервисами</li>
                    <li>чтобы со мной могли связаться (поддержка, уведомления)</li>
                    <li>чтобы мне могли оказать услугу</li>
                    <li>чтобы улучшать сервисы, для статистики и соблюдения законов</li>
                  </ul>

                  <p className="pt-1"><b>Срок действия согласия:</b> с момента предоставления до момента отзыва.</p>
                  <p>
                    Я могу отозвать это согласие в любой момент, написав на почту <a href={`mailto:${requisitesData.email}`} className="text-shanti-green underline">{requisitesData.email}</a> с пометкой <i>«Отзыв согласия на обработку персональных данных»</i>.
                  </p>
                </div>
              </div>
            )}

            {activeTab === "marketing" && (
              <div className="space-y-4">
                <div className="text-center pb-3 border-b border-shanti-earth">
                  <h2 className="font-serif font-bold text-base sm:text-lg text-shanti-dark uppercase tracking-tight">
                    СОГЛАСИЕ НА ПОЛУЧЕНИЕ РАССЫЛКИ И РЕКЛАМНЫХ МАТЕРИАЛОВ
                  </h2>
                  <p className="font-serif italic text-shanti-olive text-xs mt-1">
                    Федеральный закон № 38-ФЗ «О рекламе»
                  </p>
                </div>

                <div className="space-y-3 text-justify">
                  <p>
                    Я, регистрируясь или вводя свои данные на сайте, в боте или любом другом сервисе, добровольно и в своем интересе даю согласие Индивидуальному предпринимателю Киселеву Артуру Пшимаховичу (ИНН {requisitesData.inn}, ОГРН {requisitesData.ogrn}, адрес: {requisitesData.address}) на получение рассылки материалов рекламного или информационного характера.
                  </p>
                  <p>
                    Рассылка может осуществляться через SMS, электронную почту, WhatsApp или Telegram.
                  </p>

                  <div className="bg-shanti-light p-4 rounded-xl border border-shanti-earth space-y-1">
                    <p className="font-bold text-shanti-dark">Цель рассылки:</p>
                    <ul className="list-disc list-inside pl-1 space-y-1 text-xs">
                      <li>новости и информация о продуктах и услугах</li>
                      <li>специальные предложения, акции, скидки, бонусы</li>
                      <li>информация о мероприятиях и презентациях</li>
                    </ul>
                  </div>

                  <p>
                    Согласие действует бессрочно либо до момента его отзыва путем перехода по ссылке отписки в письме или отправки запроса на почту <a href={`mailto:${requisitesData.email}`} className="text-shanti-green underline">{requisitesData.email}</a>.
                  </p>
                </div>
              </div>
            )}

            {/* Requisites Footer Card */}
            <div className="mt-6 p-4 rounded-2xl bg-shanti-earth/20 border border-shanti-earth/80 space-y-2">
              <div className="flex items-center gap-2 font-serif font-bold text-shanti-dark text-xs uppercase tracking-wider text-shanti-green">
                <ShieldCheck className="w-4 h-4 text-shanti-green shrink-0" />
                <span>Официальные контакты и реквизиты:</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-shanti-dark font-mono pt-1">
                <p><b>Оператор:</b> {requisitesData.companyName}</p>
                <p><b>ИНН:</b> {requisitesData.inn} | <b>ОГРНИП:</b> {requisitesData.ogrn}</p>
                <p className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5 text-shanti-green shrink-0" /> {requisitesData.address}</p>
                <p className="flex items-center gap-1"><Phone className="w-3.5 h-3.5 text-shanti-green shrink-0" /> {requisitesData.phone}</p>
                <p className="flex items-center gap-1 col-span-1 sm:col-span-2"><Mail className="w-3.5 h-3.5 text-shanti-green shrink-0" /> {requisitesData.email}</p>
              </div>
            </div>
          </div>

          {/* Footer Action */}
          <div className="p-4 bg-shanti-light border-t border-shanti-earth flex items-center justify-between shrink-0">
            <span className="text-[11px] text-shanti-olive font-sans">
              ИП Киселев А.П. © 2026
            </span>
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2.5 bg-shanti-green text-white text-xs font-bold rounded-full hover:bg-shanti-olive transition-colors cursor-pointer flex items-center gap-1.5"
            >
              <Check className="w-4 h-4" />
              <span>Ознакомлен</span>
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default LegalDocumentsModal;

# Онтология оценки кредитоспособности

Готовый файл: `credit_ontology.owl` (RDF/XML, OWL 2 DL). Источники схемы — только `concept_map.mmd` и структурный учебный образец `medic44.owl`. Интернет-источники, банковские пороги, ML, правила одобрения и интерфейс не используются.

## Модель и семантические решения

Оценка связывает одного заемщика с шестью записями: личные данные, доходы и занятость, расходы, запрашиваемый кредит, кредитная история и финансовые показатели. Это контекст одной оценки; разные оценки одного лица могут содержать разные сведения. `Borrower` — необходимый структурный носитель понятия заемщика из карты. Числа и тексты — DataProperties, записи — Classes, связи записей — ObjectProperties, вымышленные лица и их записи — NamedIndividuals.

Из `medic44.owl` заимствованы самостоятельный IRI, RDF/XML, разделение классов/двух видов свойств/экземпляров, явные Domain и Range, типизированные литералы и аннотации. Медицинские сущности и характеристики отношений не импортируются. Симметричность, транзитивность и обратная функциональность не копируются: для наших отношений они не обоснованы.

Подписи «состоит из», «включает», «опирается на» не являются именами OWL-свойств. «Тип занятости → является видом → работа по найму» исправлено: виды занятости — подклассы Employment. Виды записей занятости несовместны, но один человек может иметь несколько записей разных видов. Стаж — две характеристики, а не самостоятельный объект. Активные кредиты, просрочки, предыдущие кредиты представлены количествами; отдельные договоры и события карта не детализирует. Дополнительные источники дохода — многозначный текст и отдельная совокупная месячная сумма. Семейное положение, образование, регион, регулярность и цель — строки; внешние классификаторы не вводятся.

DTI = monthlyDebtPayments / monthlyIncome. Значение хранится долей, не процентом: 0.25 = 25%. Остаток задолженности — отдельная сумма, не числитель DTI. monthlyDebtPayments добавлено как прямо требуемое заданием уточнение. monthlyIncome = officialMonthlyIncome + additionalMonthlyIncome без двойного учета; суммы доходов приведены к одному месяцу. Платеж по еще не выданному кредиту не включается: процентная ставка и расчет такого платежа отсутствуют в карте. Источники DTI заданы hasDtiIncomeBasis и hasDtiPaymentBasis. Внешний скрипт проверяет, что это записи той же оценки. При нулевом доходе dtiRatio отсутствует; DTI может превышать 1. OWL не вычисляет деление и суммы.

## Классы и иерархия

| Класс | Русское название | Родитель |
|---|---|---|
| `Borrower` | Заемщик | `owl:Thing` |
| `CreditworthinessAssessment` | Оценка кредитоспособности | `owl:Thing` |
| `PersonalData` | Данные заемщика | `owl:Thing` |
| `IncomeEmployment` | Доходы и занятость | `owl:Thing` |
| `Employment` | Занятость | `owl:Thing` |
| `SalariedEmployment` | Работа по найму | `Employment` |
| `IndividualEntrepreneurship` | Индивидуальное предпринимательство | `Employment` |
| `SelfEmployment` | Самозанятость | `Employment` |
| `Expenses` | Траты заемщика | `owl:Thing` |
| `RequestedLoan` | Характеристики запрашиваемого кредита | `owl:Thing` |
| `CreditHistory` | Кредитная история | `owl:Thing` |
| `PaymentHistory` | История выплат | `owl:Thing` |
| `CreditRating` | Кредитный рейтинг (БКИ) | `owl:Thing` |
| `CurrentCreditLoad` | Текущая кредитная нагрузка | `owl:Thing` |
| `FinancialIndicators` | Финансовые показатели | `owl:Thing` |
| `Savings` | Наличие сбережений | `owl:Thing` |
| `IncomeStability` | Регулярность и стабильность доходов | `owl:Thing` |

## Объектные свойства

| Свойство | Domain → Range | Название |
|---|---|---|
| `assessesBorrower` | CreditworthinessAssessment → Borrower | оценивает заемщика |
| `hasPersonalData` | CreditworthinessAssessment → PersonalData | использует данные заемщика |
| `hasIncomeEmployment` | CreditworthinessAssessment → IncomeEmployment | использует сведения о доходах и занятости |
| `hasExpenses` | CreditworthinessAssessment → Expenses | учитывает траты |
| `hasRequestedLoan` | CreditworthinessAssessment → RequestedLoan | рассматривает запрашиваемый кредит |
| `hasCreditHistory` | CreditworthinessAssessment → CreditHistory | использует кредитную историю |
| `hasFinancialIndicators` | CreditworthinessAssessment → FinancialIndicators | использует финансовые показатели |
| `hasEmployment` | IncomeEmployment → Employment | имеет запись о занятости |
| `hasPaymentHistory` | CreditHistory → PaymentHistory | имеет историю выплат |
| `hasCreditRating` | CreditHistory → CreditRating | имеет рейтинг БКИ |
| `hasCurrentCreditLoad` | CreditHistory → CurrentCreditLoad | имеет текущую кредитную нагрузку |
| `hasSavings` | FinancialIndicators → Savings | имеет сведения о сбережениях |
| `hasIncomeStability` | FinancialIndicators → IncomeStability | имеет характеристики стабильности доходов |
| `hasDtiIncomeBasis` | FinancialIndicators → IncomeEmployment | использует месячный доход для DTI |
| `hasDtiPaymentBasis` | FinancialIndicators → CurrentCreditLoad | использует месячные долговые платежи для DTI |

## Свойства данных

Денежные значения — рубли, потоки — рубли в месяц; возраст — полные годы, сроки и стаж — месяцы. Типы и единицы описаны также в rdfs:comment. Все свойства имеют английские camelCase-идентификаторы и rdfs:label@ru.

| Свойство | Domain | Range | Название |
|---|---|---|---|
| `ageYears` | PersonalData | xsd:nonNegativeInteger | возраст в годах |
| `maritalStatus` | PersonalData | xsd:string | семейное положение |
| `education` | PersonalData | xsd:string | образование |
| `residenceRegion` | PersonalData | xsd:string | регион проживания |
| `monthlyIncome` | IncomeEmployment | decimal ≥ 0 | совокупный месячный доход |
| `officialMonthlyIncome` | IncomeEmployment | decimal ≥ 0 | официальный месячный доход |
| `additionalMonthlyIncome` | IncomeEmployment | decimal ≥ 0 | совокупный дополнительный месячный доход |
| `additionalIncomeSource` | IncomeEmployment | xsd:string | дополнительный источник дохода |
| `totalWorkExperienceMonths` | IncomeEmployment | xsd:nonNegativeInteger | общий стаж в месяцах |
| `currentWorkExperienceMonths` | Employment | xsd:nonNegativeInteger | стаж на текущем месте в месяцах |
| `monthlyUtilities` | Expenses | decimal ≥ 0 | месячная оплата ЖКХ |
| `monthlyRent` | Expenses | decimal ≥ 0 | месячная аренда жилья |
| `monthlyOtherExpenses` | Expenses | decimal ≥ 0 | прочие регулярные месячные расходы |
| `monthlyCommunication` | Expenses | decimal ≥ 0 | месячные расходы на связь и интернет |
| `monthlyTransport` | Expenses | decimal ≥ 0 | месячные транспортные расходы |
| `monthlyFood` | Expenses | decimal ≥ 0 | месячные расходы на питание |
| `dependentCount` | Expenses | xsd:nonNegativeInteger | количество иждивенцев |
| `requestedAmount` | RequestedLoan | decimal > 0 | запрашиваемая сумма кредита |
| `termMonths` | RequestedLoan | xsd:positiveInteger | срок кредита в месяцах |
| `loanPurpose` | RequestedLoan | xsd:string | цель кредита |
| `previousLoanCount` | CreditHistory | xsd:nonNegativeInteger | количество предыдущих кредитов |
| `overdueCount` | PaymentHistory | xsd:nonNegativeInteger | количество просрочек |
| `creditHistoryMonths` | PaymentHistory | xsd:nonNegativeInteger | длительность кредитной истории в месяцах |
| `paymentRegularity` | PaymentHistory | xsd:string | регулярность платежей |
| `bureauScore` | CreditRating | xsd:nonNegativeInteger | скоринговый балл из БКИ |
| `activeLoanCount` | CurrentCreditLoad | xsd:nonNegativeInteger | количество активных кредитов |
| `outstandingDebt` | CurrentCreditLoad | decimal ≥ 0 | остаток задолженности |
| `monthlyDebtPayments` | CurrentCreditLoad | decimal ≥ 0 | ежемесячные платежи по долговым обязательствам |
| `dtiRatio` | FinancialIndicators | decimal ≥ 0 | соотношение долга к доходу (DTI) |
| `hasSavingsAvailable` | Savings | xsd:boolean | наличие сбережений |
| `accountBalance` | Savings | decimal ≥ 0 | остатки на счетах |
| `hasAssets` | Savings | xsd:boolean | наличие активов |
| `incomeVolatility` | IncomeStability | xsd:string | волатильность доходов |
| `incomePeriodicity` | IncomeStability | xsd:string | периодичность поступлений |

## Ограничения

Корневые классы попарно несовместны (AllDisjointClasses); три подкласса Employment также несовместны. Скалярные свойства функциональны. Для обязательных полей и одиночных ссылок установлено ровно одно значение соответствующего типа; для hasEmployment — someValuesFrom (минимум одна запись). additionalIncomeSource многозначно и необязательно; dtiRatio функционально и необязательно из-за нулевого дохода. Числа неотрицательны, сумма кредита строго положительна, срок — positiveInteger. Никаких порогов возраста, БКИ или DTI для одобрения нет. AllDifferent различает все демонстрационные объекты.

OWL использует открытый мир: отсутствие обязательного утверждения само по себе не означает противоречия, reasoner допускает неизвестное значение. Поэтому полнота примеров и межполевая арифметика проверяются отдельно. Domain/Range — логические аксиомы вывода типов, а не формы проверки ввода. Согласованность не доказывает фактическую достоверность вымышленных данных.

## Экземпляры

Создано 140 NamedIndividuals: 10 заемщиков borrower01…borrower10, 10 оценок и связанные записи. Имена лиц не собираются: метки «Вымышленный заемщик 01» достаточны для идентификации примеров. Различаются возраст, занятость, доход, регион, расходы, иждивенцы, история, БКИ, нагрузка, сбережения, активы и параметры кредита. Есть отсутствие предыдущих кредитов, отсутствие активных долгов, нулевые сбережения, просрочки и DTI выше 1. Все значения синтетические.

| Заемщик | Возраст | Месячный доход | Месячные долговые платежи | Остаток долга | DTI (доля) | Вид занятости |
|---|---:|---:|---:|---:|---:|---|
| borrower01 | 24 | 55000 | 0 | 0 | 0.000000 | SalariedEmployment |
| borrower02 | 32 | 130000 | 18000 | 450000 | 0.138462 | SalariedEmployment |
| borrower03 | 41 | 125000 | 32000 | 1100000 | 0.256000 | IndividualEntrepreneurship |
| borrower04 | 29 | 85000 | 9000 | 170000 | 0.105882 | SelfEmployment |
| borrower05 | 53 | 70000 | 28000 | 520000 | 0.400000 | SalariedEmployment |
| borrower06 | 37 | 180000 | 45000 | 1500000 | 0.250000 | IndividualEntrepreneurship |
| borrower07 | 22 | 38000 | 7000 | 95000 | 0.184211 | SalariedEmployment |
| borrower08 | 46 | 170000 | 0 | 0 | 0.000000 | SalariedEmployment |
| borrower09 | 35 | 80000 | 42000 | 800000 | 0.525000 | SalariedEmployment |
| borrower10 | 60 | 60000 | 65000 | 900000 | 1.083333 | SalariedEmployment |

## Полное соответствие узлов карты

Проанализировано 48 узлов и 49 связей. Группирующие узлы не обязаны становиться отдельными классами.

| Узел | Понятие карты | Реализация |
|---|---|---|
| MAIN | Оценка кредитоспособности для выдачи потребительского кредита | CreditworthinessAssessment |
| DATA | Данные заемщика | PersonalData |
| AGE | Возраст | ageYears |
| FAMILY | Семейное положение | maritalStatus |
| EDUCATION | Образование | education |
| REGION | Регион проживания | residenceRegion |
| EMP | Доходы и занятость | IncomeEmployment |
| INCOME | Уровень дохода | monthlyIncome |
| OFFICIAL | Официальный доход | officialMonthlyIncome |
| ADDITIONAL | Дополнительные источники дохода | additionalIncomeSource |
| TYPE | Тип занятости | Employment |
| EMPLOYEE | Работа по найму | SalariedEmployment |
| BUSINESS | Индивидуальное предпринимательство | IndividualEntrepreneurship |
| SELF | Самозанятость | SelfEmployment |
| EXPERIENCE | Стаж работы | totalWorkExperienceMonths, currentWorkExperienceMonths |
| TOTAL | Общий стаж | totalWorkExperienceMonths |
| CURRENT | Стаж на текущем месте работы | currentWorkExperienceMonths |
| EXPENSES | Траты заемщика | Expenses |
| UTILITIES | Оплата ЖКХ | monthlyUtilities |
| RENT | Аренда жилья | monthlyRent |
| OTHER | Прочие регулярные расходы | monthlyOtherExpenses |
| DEPENDENTS | Количество иждивенцев | dependentCount |
| COMMUNICATION | Связь и интернет | monthlyCommunication |
| TRANSPORT | Транспортные расходы | monthlyTransport |
| FOOD | Питание | monthlyFood |
| LOAN | Характеристики запрашиваемого кредита | RequestedLoan |
| AMOUNT | Сумма кредита | requestedAmount |
| TERM | Срок кредита | termMonths |
| PURPOSE | Цель кредита | loanPurpose |
| HISTORY | Кредитная история | CreditHistory |
| PREVIOUS | Количество предыдущих кредитов | previousLoanCount |
| PAYMENTS | История выплат | PaymentHistory |
| DELAYS | Просрочки | overdueCount |
| DURATION | Длительность кредитной истории | creditHistoryMonths |
| REGULARITY | Регулярность платежей | paymentRegularity |
| RATING | Кредитный рейтинг (БКИ) | CreditRating |
| SCORE | Скоринговый балл из БКИ | bureauScore |
| LOAD | Текущая кредитная нагрузка | CurrentCreditLoad |
| ACTIVE | Активные кредиты | activeLoanCount |
| DEBT | Остаток задолженности | outstandingDebt |
| FINANCE | Финансовые показатели | FinancialIndicators |
| DTI | Соотношение долга к доходу (DTI) | dtiRatio |
| SAVINGS | Наличие сбережений | Savings |
| ACCOUNTS | Остатки на счетах | accountBalance |
| ASSETS | Наличие активов | hasAssets |
| STABILITY | Регулярность и стабильность доходов | IncomeStability |
| VOLATILITY | Волатильность доходов | incomeVolatility |
| PERIODICITY | Периодичность поступлений | incomePeriodicity |

## Разбор всех связей карты

| Связь карты | Семантическая реализация |
|---|---|
| MAIN — состоит из → DATA | hasPersonalData |
| DATA — включает → AGE | ageYears — характеристика соответствующей записи |
| DATA — включает → FAMILY | maritalStatus — характеристика соответствующей записи |
| DATA — включает → EDUCATION | education — характеристика соответствующей записи |
| DATA — включает → REGION | residenceRegion — характеристика соответствующей записи |
| MAIN — состоит из → EMP | hasIncomeEmployment |
| EMP — включает → INCOME | monthlyIncome — характеристика соответствующей записи |
| EMP — включает → TYPE | hasEmployment |
| EMP — включает → EXPERIENCE | totalWorkExperienceMonths у IncomeEmployment; currentWorkExperienceMonths через hasEmployment |
| INCOME — состоит из → OFFICIAL | officialMonthlyIncome — характеристика соответствующей записи |
| INCOME — состоит из → ADDITIONAL | additionalIncomeSource — характеристика соответствующей записи |
| TYPE — является видом → EMPLOYEE | SalariedEmployment SubClassOf Employment (направление карты исправлено) |
| TYPE — является видом → BUSINESS | IndividualEntrepreneurship SubClassOf Employment (направление карты исправлено) |
| TYPE — является видом → SELF | SelfEmployment SubClassOf Employment (направление карты исправлено) |
| EXPERIENCE — состоит из → TOTAL | totalWorkExperienceMonths у IncomeEmployment |
| EXPERIENCE — состоит из → CURRENT | currentWorkExperienceMonths у Employment |
| MAIN — состоит из → EXPENSES | hasExpenses |
| EXPENSES — включает → UTILITIES | monthlyUtilities — характеристика соответствующей записи |
| EXPENSES — включает → RENT | monthlyRent — характеристика соответствующей записи |
| EXPENSES — включает → OTHER | monthlyOtherExpenses — характеристика соответствующей записи |
| EXPENSES — учитывает → DEPENDENTS | dependentCount — характеристика соответствующей записи |
| EXPENSES — включает → COMMUNICATION | monthlyCommunication — характеристика соответствующей записи |
| EXPENSES — включает → TRANSPORT | monthlyTransport — характеристика соответствующей записи |
| EXPENSES — включает → FOOD | monthlyFood — характеристика соответствующей записи |
| MAIN — состоит из → LOAN | hasRequestedLoan |
| LOAN — включает → AMOUNT | requestedAmount — характеристика соответствующей записи |
| LOAN — включает → TERM | termMonths — характеристика соответствующей записи |
| LOAN — включает → PURPOSE | loanPurpose — характеристика соответствующей записи |
| MAIN — состоит из → HISTORY | hasCreditHistory |
| HISTORY — характеризуется → PREVIOUS | previousLoanCount — характеристика соответствующей записи |
| HISTORY — включает → PAYMENTS | hasPaymentHistory |
| HISTORY — включает → RATING | hasCreditRating |
| HISTORY — включает → LOAD | hasCurrentCreditLoad |
| PAYMENTS — содержит → DELAYS | overdueCount — характеристика соответствующей записи |
| PAYMENTS — содержит → DURATION | creditHistoryMonths — характеристика соответствующей записи |
| PAYMENTS — содержит → REGULARITY | paymentRegularity — характеристика соответствующей записи |
| RATING — содержит → SCORE | bureauScore — характеристика соответствующей записи |
| LOAD — состоит из → ACTIVE | activeLoanCount — характеристика соответствующей записи |
| LOAD — состоит из → DEBT | outstandingDebt — характеристика соответствующей записи |
| MAIN — состоит из → FINANCE | hasFinancialIndicators |
| FINANCE — включает → DTI | dtiRatio — характеристика соответствующей записи |
| FINANCE — включает → SAVINGS | hasSavings |
| FINANCE — включает → STABILITY | hasIncomeStability |
| SAVINGS — состоит из → ACCOUNTS | accountBalance — характеристика соответствующей записи |
| SAVINGS — состоит из → ASSETS | hasAssets — характеристика соответствующей записи |
| STABILITY — характеризуется → VOLATILITY | incomeVolatility — характеристика соответствующей записи |
| STABILITY — характеризуется → PERIODICITY | incomePeriodicity — характеристика соответствующей записи |
| DTI — опирается на → INCOME | hasDtiIncomeBasis → monthlyIncome (знаменатель) |
| DTI — опирается на → DEBT | hasDtiPaymentBasis → monthlyDebtPayments (числитель); outstandingDebt сохраняется отдельно, прямая зависимость отвергнута |

## Открытие в Protégé

1. Запустите Protégé (в проекте есть Protege-5.0.0).
2. Выберите File → Open и откройте credit_ontology.owl. Импорты и доступ к сети не нужны.
3. Во вкладках Classes, Object properties, Data properties и Individuals изучите сущности. В Entities при необходимости включите отображение по rdfs:label.
4. Выберите Reasoner → HermiT → Start reasoner. Убедитесь, что нет сообщения о несогласованности, а под owl:Nothing нет именованных классов.
5. Откройте assessment01 или borrower01 и проследите объектные связи; характеристики находятся у связанных записей оценки.

## Воспроизведение и проверка

Python-зависимости: rdflib==7.6.0 и owlready2==0.51; для HermiT нужна Java (скрипт использует JRE из поставки Protégé).

```powershell
python -m pip install rdflib==7.6.0 owlready2==0.51
python build_credit_ontology.py
python validate_credit_ontology.py
```

Генератор пересоздает OWL и README. Проверяющий скрипт не изменяет онтологию: проверяет RDF/XML, покрытие карты, структуру, полноту утверждений, ограничения значений и арифметику. Затем HermiT проверяет полную онтологию с экземплярами. Через Java 8 Nashorn (jjs из поставки Protégé) и вспомогательный check_owl_profile.js дополнительно выполняются формальная проверка OWLAPI OWL2DLProfile и независимая загрузка исходного RDF/XML напрямую в HermiT. При отсутствии jjs формальная проверка помечается как не выполненная.

Фактический результат записан в validation_report.json: синтаксис корректен, OWL2DLProfile пройден, полная онтология согласованна, неудовлетворимых именованных классов нет; арифметика и заполненность примеров проверены. Отчет содержит SHA-256 проверенного OWL и версии библиотек. OWL-арифметика не подменяется логическим выводом: суммы и DTI проверяет Python.

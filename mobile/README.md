# Лабораторная работа 2 — «Контактные данные»

Приложение на Kotlin с XML-разметкой, minimum SDK 26 (Android 8.0).
Две Activity используют общий ViewModel. Контакты можно добавлять, изменять, удалять и просматривать стрелками. Данные сохраняются после перезапуска.

## Какие файлы за что отвечают

Основной код находится в `app/src/main/java/com/example/lab2/`.

| Файл | Назначение |
| --- | --- |
| MainActivity.kt | Главный экран. Обрабатывает нажатия кнопок и стрелок. `openEditor()` открывает форму, `showContact()` показывает контакт и обновляет доступность кнопок. `onResume()` обновляет экран после возврата из формы. |
| EditContactActivity.kt | Экран ввода и изменения. Получает режим через Intent (`edit`). При нажатии «Сохранить» проверяет поля, создаёт Contact, вызывает `add()` или `update()` и закрывается через `finish()`. |
| Contact.kt | Data class с четырьмя полями: фамилия, имя, отчество и телефон. |
| ContactsViewModel.kt | Хранит список `contacts` и текущий индекс `index`. Методы `add()`, `update()`, `delete()` меняют список. `save()` записывает JSON в SharedPreferences, `load()` загружает его. |
| ContactsApp.kt | Общий владелец ViewModel для обеих Activity. Создаёт один экземпляр через ViewModelProvider и вызывает загрузку сохранённых контактов. |

В `app/src/main/` также находятся:

- `res/layout/activity_main.xml` — расположение элементов главного экрана.
- `res/layout/activity_edit_contact.xml` — четыре поля ввода и кнопки формы.
- `res/values/strings.xml` — название приложения, надписи и сообщения.
- `res/values/themes.xml` и `res/values-night/themes.xml` — оформление для светлой и тёмной темы.
- `res/drawable/ic_previous.xml` и `ic_next.xml` — стрелки; остальные иконки используются для значка приложения.
- `AndroidManifest.xml` — регистрирует ContactsApp и обе Activity; MainActivity запускается первой.

`app/build.gradle.kts` задаёт SDK и зависимости приложения, `gradle/libs.versions.toml` — их версии. Gradle Wrapper (`gradlew`, `gradlew.bat`, `gradle/wrapper/`) запускает сборку.
`local.properties` содержит путь к установленному Android SDK.

## Основные действия

1. При запуске ContactsApp получает общий ViewModel и загружает контакты из SharedPreferences.
2. «Добавить» / «Изменить» в MainActivity открывают EditContactActivity через Intent. В Intent передаётся только режим; сами контакты доступны через общий ViewModel.
3. «Сохранить» в форме проверяет фамилию, имя и телефон. Затем `add()` добавляет контакт или `update()` заменяет текущий. Оба метода вызывают `save()`.
4. После `finish()` главный экран в `onResume()` вызывает `showContact()`.
5. Стрелки меняют `index`, после чего `showContact()` отображает выбранную запись.
6. «Удалить» вызывает `delete()`: запись удаляется, индекс исправляется и список сохраняется.

ViewModel хранит данные в памяти и сохраняется при повороте экрана. Постоянное хранение после завершения процесса обеспечивает SharedPreferences: список записывается строкой JSON в закрытое хранилище приложения. Очистка данных приложения или его удаление стирают контакты.

## Запуск на MuMu

Запустить MuMu и выполнить в PowerShell терминала Android Studio:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" connect 127.0.0.1:16384
```

Выбрать устройство MuMu / ALT-AL10, конфигурацию `app` и нажать Run.
Для Gradle используется встроенная Java Android Studio (jbr, Java 21).

## Проверки

- `ContactsViewModelTest.kt` в `app/src/test/` проверяет добавление, изменение и удаление.
- `ContactsFlowTest.kt` в `app/src/androidTest/` проверяет действия на экране.
- `ContactsStorageTest.kt` там же проверяет сохранение и загрузку через отдельный тестовый файл SharedPreferences.

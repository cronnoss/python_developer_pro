### MemcLoad v2
*Задание:* нужно переписать Python версию memc_load на Go. Программа по-прежнему парсит и заливает в мемкеш поминутную выгрузку логов трекера установленных приложений. Ключом является тип и идентификатор устройства через двоеточие, значением являет protobuf сообщение (https://github.com/golang/protobuf).


Пример tsv-файла:
```
$ gunzip -c sample.tsv.gz | head -3
idfa    1rfw452y52g2gq4g        55.55   42.42   1423,43,567,3,7,23
idfa    2rfw452y52g2gq4g        55.55   42.42   2423,43,567,3,7,23
idfa    3rfw452y52g2gq4g        55.55   42.42   3423,43,567,3,7,23
```

Подготовка к запуску:
1. Установить компилятор GO
2. Инициализировать проект: ```go mod init hw_17```
3. Установить зависимости:
    ```
    go get github.com/bradfitz/gomemcache/memcache
    go get google.golang.org/protobuf/proto
    go get github.com/golang/protobuf/ptypes
    go get github.com/golang/protobuf/ptypes/any
    ```
4. Сгенерировать appsinstalled.pb.go из appsinstalled.proto:
   ```
   protoc --go_out=. --go_opt=paths=source_relative appsinstalled.proto
   ```
5. Переместить сгенерированный файл appsinstalled.pb.goв папку appsinstalled/

6. Скомпилировать проект:
   ```
   go build
   ```   
Запустить проект на выполнение:
```
./hw_17 -pattern "./*.tsv.gz" -dry
``` 
или в Windows:
```
hw_17.exe -pattern "./*.tsv.gz" -dry
```

Результат работы скрипта:
```
 ./hw_17 -pattern "./*.tsv.gz" -dry
2026/01/04 20:02:03 Using pattern: ./*.tsv.gz
2026/01/04 20:02:03 Found 1 file(s)
2026/01/04 20:02:03 Dry run: idfa:1rfw452y52g2gq4g - apps:1423 apps:43 apps:567 apps:3 apps:7 apps:23 lat:55.55 lon:42.42
2026/01/04 20:02:03 Dry run: idfa:2rfw452y52g2gq4g - apps:2423 apps:43 apps:567 apps:3 apps:7 apps:23 lat:55.55 lon:42.42
2026/01/04 20:02:03 Dry run: idfa:3rfw452y52g2gq4g - apps:3423 apps:43 apps:567 apps:3 apps:7 apps:23 lat:55.55 lon:42.42
2026/01/04 20:02:03 Dry run: idfa:4rfw452y52g2gq4g - apps:4423 apps:43 apps:567 apps:3 apps:7 apps:23 lat:55.55 lon:42.42
2026/01/04 20:02:03 Dry run: idfa:5rfw452y52g2gq4g - apps:5423 apps:43 apps:567 apps:3 apps:7 apps:23 lat:55.55 lon:42.42
2026/01/04 20:02:03 Dry run: gaid:6rfw452y52g2gq4g - apps:6423 apps:43 apps:567 apps:3 apps:7 apps:23 lat:55.55 lon:42.42
2026/01/04 20:02:03 Dry run: gaid:7rfw452y52g2gq4g - apps:7423 apps:43 apps:567 apps:3 apps:7 apps:23 lat:55.55 lon:42.42
2026/01/04 20:02:03 Dry run: gaid:8rfw452y52g2gq4g - apps:8423 apps:43 apps:567 apps:3 apps:7 apps:23 lat:55.55 lon:42.42
2026/01/04 20:02:03 Dry run: gaid:9rfw452y52g2gq4g - apps:9423 apps:43 apps:567 apps:3 apps:7 apps:23 lat:55.55 lon:42.42
2026/01/04 20:02:03 Dry run: gaid:10fw452y52g2gq4g - apps:1023 apps:43 apps:567 apps:3 apps:7 apps:23 lat:55.55 lon:42.42
2026/01/04 20:02:03 Processed 10 entries successfully
2026/01/04 20:02:03 Finished processing files

```
Файл обрабатывается, после обработки к имени файла добавляется префикс-точка.


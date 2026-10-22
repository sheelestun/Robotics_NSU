# Источник задания PR06

- Страница: https://ros.lms.ci.nsu.ru/practices/pr06 (неделя 06, «Модель робота, tf2 и QoS преобразований»).
- Точная дата первой публикации на странице не указана. Лента изменений курса датирует добавление обязательного `tf-qos.txt` 12 октября 2026 года: https://ros.lms.ci.nsu.ru/course/changes.
- Проверенный архив: `v1-w07`, SHA-256 `9b7fdd5424d3d97e47d51dbe23064934585e62135dc2902844dd679529bda929`. Вход: `models/course_ackermann/model.sdf`; манифест: `practices/manifests/pr06.json`.
- Контракт: пакет `course_description`, `urdf/vehicle.urdf.xacro`, launch и тесты; параметры базы, колеи и радиуса колеса; связное дерево `base_link`, `camera_link`, `lidar_link`, `imu_link`; отдельные visual/collision; `robot_state_publisher` и RViz; поздние подписчики `/tf_static` с `transient_local` и `volatile`; дефект parent лидара `camera_link` вместо `base_link`, падение и исправление теста; `frames.md`, `model-check.txt`, `tf-qos.txt`, `report.json`, запись в `AI_USAGE.md`.
- Манифест требует claims `public_tests_passed`, `defect_reproduced`, `defect_fixed`. Проверка `check_practice.py PR06`.

# PR06: статические системы координат

Источник размеров: `.course-kit/v1/models/course_ackermann/model.sdf`, kit `v1-w07` (SHA-256 архива `9b7fdd5424d3d97e47d51dbe23064934585e62135dc2902844dd679529bda929`). Оси REP-103: X вперёд, Y влево, Z вверх. Все величины в СИ.

| Parent | Child | Смещение XYZ, м | Поворот RPY, рад | Владелец |
| --- | --- | --- | --- | --- |
| `base_link` | `camera_link` | `0.28 0 0.38` | `0 0 0` | `robot_state_publisher` |
| `base_link` | `lidar_link` | `0.28 0 0.38` | `0 0 0` | `robot_state_publisher` |
| `base_link` | `imu_link` | `0.28 0 0.38` | `0 0 0` | `robot_state_publisher` |
| `base_link` | `front_left_wheel_link` | `0.4 0.31 0` | `0 0 0` | `robot_state_publisher` |
| `base_link` | `front_right_wheel_link` | `0.4 -0.31 0` | `0 0 0` | `robot_state_publisher` |
| `base_link` | `rear_left_wheel_link` | `-0.4 0.31 0` | `0 0 0` | `robot_state_publisher` |
| `base_link` | `rear_right_wheel_link` | `-0.4 -0.31 0` | `0 0 0` | `robot_state_publisher` |

Колёса в этом ROS-описании закреплены фиксированно: обязательная проверка PR06 касается дерева датчиков, а физика руления остаётся в отдельной SDF-модели PR07. В живой проверке `tf2_echo base_link lidar_link` дал `(0.280, 0.000, 0.380)` и единичный поворот. Временная замена parent лидара на `camera_link` при прежнем offset дала бы суммарное смещение `(0.56, 0, 0.76)`; тест ожидаемого parent упал, затем после возврата связи прошёл. Подробный вывод — `model-check.txt`.

# PR04 — параметры движения

Проверка выполнена в контейнере `pr01-student-demo` с ROS 2 Lyrical. Нода запущена командой:

```bash
source /opt/ros/lyrical/setup.bash
source /work/robototechniks/install/setup.bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

## Значения по умолчанию

```console
$ ros2 param get /patrol linear_speed
Double value is: 0.5
$ ros2 param get /patrol turn_rate
Double value is: 0.3
$ ros2 param get /patrol publish_hz
Double value is: 10.0
```

До изменения частоты `ros2 topic hz /turtle1/cmd_vel --window 20` показал `average rate: 9.999`. После команды:

```console
$ ros2 param set /patrol publish_hz 5.0
Set parameter successful
$ ros2 topic hz /turtle1/cmd_vel --window 20
average rate: 5.000
```

Старый таймер отменяется и удаляется до создания нового, поэтому после изменения остаётся один поток с частотой 5 Гц.

## Недопустимые значения

```console
$ ros2 param set /patrol publish_hz 0.0
Setting parameter failed: publish_hz must be finite and between 1.0 and 30.0 Hz
$ ros2 param get /patrol publish_hz
Double value is: 5.0

$ ros2 param set /patrol publish_hz -- -1.0
Setting parameter failed: publish_hz must be finite and between 1.0 and 30.0 Hz
$ ros2 param get /patrol publish_hz
Double value is: 5.0

$ ros2 param set /patrol publish_hz .nan
Setting parameter failed: publish_hz must be finite and between 1.0 and 30.0 Hz
$ ros2 param get /patrol publish_hz
Double value is: 5.0
```

Во всех трёх случаях нода продолжила работать, а активная частота сохранилась.

## Скорость и поворот

```console
$ ros2 param set /patrol linear_speed 0.8
Set parameter successful
$ ros2 param set /patrol turn_rate -0.4
Set parameter successful
$ ros2 topic echo /turtle1/cmd_vel --once
linear:
  x: 0.8
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: -0.4
```

## Воспроизведение и исправление дефекта

Для контролируемого воспроизведения нижняя граница проверки частоты была временно изменена с `1.0` на `0.0` без фиксации в Git. Команда `ros2 param set /patrol publish_hz 0.0` завершила ноду; в журнале зафиксирован конкретный отказ:

```text
File "patrol.py", line 132, in _apply_parameters
    1.0 / self._publish_hz,
ZeroDivisionError: division by zero
[ros2run]: Process exited with failure 1
```

После возврата проверки та же команда получила `Setting parameter failed`, значение осталось `5.0`, а `ros2 node list` по-прежнему показывал `/patrol`.

## Готовые service и action

```console
$ ros2 service call /clear std_srvs/srv/Empty '{}'
response:
std_srvs.srv.Empty_Response()
$ ros2 action list -t
/turtle1/rotate_absolute [turtlesim_msgs/action/RotateAbsolute]
```

Запрос сервиса — один вызов с одним итоговым ответом, например очистка следа через `/clear`. Цель action живёт дольше одного запроса и может передавать feedback или быть отменена до результата, как `/turtle1/rotate_absolute`.

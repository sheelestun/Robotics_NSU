# PR07: повторная проверка после переноса рабочей копии

- `ros2 launch course_simulation simulation.launch.py headless:=true` запустил Gazebo, `robot_state_publisher`, один `parameter_bridge` и два адаптера.
- `ros2 run course_simulation demo_drive` завершился с кодом 0; после маршрута `/vehicle/odom` имел `frame_id=odom`, `child_frame_id=base_link`, `position.x=2.906709169948026` и `position.y=0.48052883067913865`.
- После исправления обработки завершения оба Python-адаптера закончили работу штатно при `Ctrl+C`. У установленного `ros_gz_bridge/parameter_bridge` в этом контейнере при остановке остался `exit code -11`; во время работы доставка сообщений была подтверждена ранее. Активных процессов симуляции и адаптеров после остановки не осталось.
- `ros2 bag info fixtures/pr07-sensors`: MCAP, 78.406 с времени симуляции, 96 219 сообщений, все семь обязательных топиков непусты. Запись хранится локально и игнорируется Git.

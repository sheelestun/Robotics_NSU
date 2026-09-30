# PR03 demo

## Environment

- ROS 2 distribution: Lyrical
- Package: `patrol` (`ament_python`)
- Pose type: `turtlesim_msgs/msg/Pose`
- Command type: `geometry_msgs/msg/Twist`
- Timer period: 0.1 s

## Node lifecycle

`rclpy.init()` initializes the ROS 2 context. The pose subscription callback
stores only the latest `/turtle1/pose` message. `rclpy.spin()` dispatches the
subscription and timer callbacks. Every 0.1 s the timer publishes the result of
the pure `command_from_pose()` function.

Before the first pose, the function returns a zero `Twist`. After a pose is
available, it returns `linear.x = 0.5` and `angular.z = 0.3`.

`Ctrl+C` interrupts `spin`, after which the node is destroyed and the ROS 2
context is shut down. The disappearance of the publisher is not treated as an
instant brake: after stopping `patrol`, the experiment waited for turtlesim
and observed zero velocities and two identical poses.

## Defect reproduction

The node was first started without remapping:

```bash
ros2 run patrol patrol
```

Because `cmd_vel` is relative and the node namespace is `/`, it resolved to
`/cmd_vel`. Graph inspection showed:

```text
/cmd_vel:         Publisher count: 1, Subscription count: 0
/turtle1/cmd_vel: Publisher count: 0, Subscription count: 1
```

The subscriber on `/turtle1/cmd_vel` belonged to `turtlesim`. Two pose
samples three seconds apart were identical:

```text
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```

This reproduces the required name mismatch: the message type was correct, but
the publisher and subscriber used different fully qualified topic names.

## Remap fix

The same executable was restarted without changing its code:

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

After remapping, `/turtle1/cmd_vel` had one publisher (`patrol`) and one
subscriber (`turtlesim`). Pose samples changed from:

```text
x: 6.581179141998291
y: 5.909318923950195
theta: 0.6720147132873535
```

to:

```text
x: 3.897569417953491
y: 7.491722583770752
theta: -1.74237060546875
linear_velocity: 0.5
angular_velocity: 0.30000001192092896
```

A ten-second measurement reported an average rate of approximately 10.000 Hz,
matching the 0.1 s timer period.

After `Ctrl+C`, only `/turtlesim` remained. Following a two-second wait, two
pose samples were identical and both reported:

```text
linear_velocity: 0.0
angular_velocity: 0.0
```

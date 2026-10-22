from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


MODEL = Path(__file__).resolve().parents[1] / 'urdf' / 'vehicle.urdf.xacro'


def expanded_model():
    return ET.fromstring(subprocess.check_output(['xacro', str(MODEL)]))


def test_sensor_tree_and_expected_lidar_parent():
    robot = expanded_model()
    links = {link.attrib['name'] for link in robot.findall('link')}
    edges = {joint.find('child').attrib['link']:
             joint.find('parent').attrib['link'] for joint in robot.findall('joint')}
    assert {'base_link', 'camera_link', 'lidar_link', 'imu_link'} <= links
    assert edges['lidar_link'] == 'base_link'
    assert edges['camera_link'] == 'base_link'
    assert edges['imu_link'] == 'base_link'
    assert set(edges) == links - {'base_link'}
    for child in edges:
        visited = set()
        while child != 'base_link':
            assert child not in visited
            visited.add(child)
            child = edges[child]


def test_geometry_and_inertia():
    robot = expanded_model()
    base = robot.find("link[@name='base_link']")
    assert base.find('visual/geometry/box') is not None
    assert base.find('collision/geometry/box') is not None
    assert float(base.find('inertial/mass').attrib['value']) > 0
    inertia = base.find('inertial/inertia').attrib
    assert all(float(inertia[axis]) > 0 for axis in ('ixx', 'iyy', 'izz'))
    wheels = [link for link in robot.findall('link')
              if link.attrib['name'].endswith('_wheel_link')]
    assert len(wheels) == 4
    assert all(abs(float(link.find('visual/geometry/cylinder').attrib['radius'])
                   - 0.12) < 1e-9 for link in wheels)
    for name in ('camera_link', 'lidar_link', 'imu_link'):
        sensor = robot.find(f"link[@name='{name}']")
        assert sensor.find('visual/geometry/box') is not None
        assert sensor.find('collision/geometry/box') is not None
        assert float(sensor.find('inertial/mass').attrib['value']) > 0

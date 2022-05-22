# Originally adapted from https://github.com/thomasfermi/Algorithms-for-Automated-Driving
import math
import numpy as np

# Function from https://stackoverflow.com/a/59582674/2609987
def circle_line_segment_intersection(
    circle_center, circle_radius, pt1, pt2, full_line=True, tangent_tol=1e-9
):
    """Find the points at which a circle intersects a line-segment.  This can happen at 0, 1, or 2 points.
    :param circle_center: The (x, y) location of the circle center
    :param circle_radius: The radius of the circle
    :param pt1: The (x, y) location of the first point of the segment
    :param pt2: The (x, y) location of the second point of the segment
    :param full_line: True to find intersections along full line - not just in the segment.  False will just return intersections within the segment.
    :param tangent_tol: Numerical tolerance at which we decide the intersections are close enough to consider it a tangent
    :return Sequence[Tuple[float, float]]: A list of length 0, 1, or 2, where each element is a point at which the circle intercepts a line segment.
    Note: We follow: http://mathworld.wolfram.com/Circle-LineIntersection.html
    """

    (p1x, p1y), (p2x, p2y), (cx, cy) = pt1, pt2, circle_center
    (x1, y1), (x2, y2) = (p1x - cx, p1y - cy), (p2x - cx, p2y - cy)
    dx, dy = (x2 - x1), (y2 - y1)
    dr = (dx**2 + dy**2) ** 0.5
    big_d = x1 * y2 - x2 * y1
    discriminant = circle_radius**2 * dr**2 - big_d**2

    if discriminant < 0:  # No intersection between circle and line
        return []
    else:  # There may be 0, 1, or 2 intersections with the segment
        intersections = [
            (
                cx
                + (big_d * dy + sign * (-1 if dy < 0 else 1) * dx * discriminant**0.5)
                / dr**2,
                cy + (-big_d * dx + sign * abs(dy) * discriminant**0.5) / dr**2,
            )
            for sign in ((1, -1) if dy < 0 else (-1, 1))
        ]  # This makes sure the order along the segment is correct
        if (
            not full_line
        ):  # If only considering the segment, filter out intersections that do not fall within the segment
            fraction_along_segment = [
                (xi - p1x) / dx if abs(dx) > abs(dy) else (yi - p1y) / dy
                for xi, yi in intersections
            ]
            intersections = [
                pt
                for pt, frac in zip(intersections, fraction_along_segment)
                if 0 <= frac <= 1
            ]
        if (
            len(intersections) == 2 and abs(discriminant) <= tangent_tol
        ):  # If line is tangent to circle, return just one point (as both intersections have same location)
            return [intersections[0]]
        else:
            return intersections


def get_target_point(lookahead, polyline):
    """Determines the target point for the pure pursuit controller

    Parameters
    ----------
    lookahead : float
        The target point is on a circle of radius `lookahead`
        The circle's center is (0,0)
    poyline: array_like, shape (M,2)
        A list of 2d points that defines a polyline.

    Returns:
    --------
    target_point: numpy array, shape (,2)
        Point with positive x-coordinate where the circle of radius `lookahead`
        and the polyline intersect.
        Return None if there is no such point.
        If there are multiple such points, return the one that the polyline
        visits first.
    """
    intersections = []
    for j in range(len(polyline) - 1):
        pt1 = polyline[j]
        pt2 = polyline[j + 1]
        intersections += circle_line_segment_intersection(
            (0, 0), lookahead, pt1, pt2, full_line=False
        )
    filtered = [p for p in intersections if p[0] > 0]
    if len(filtered) == 0:
        return None
    return filtered[0]


class PurePursuit:
    def __init__(self, K_dd=0.4, wheel_base=2.65):
        self.K_dd = K_dd
        self.wheel_base = wheel_base

    def get_control(self, waypoints, speed):
        # transform x coordinates of waypoints such that coordinate origin is in rear wheel
        look_ahead_distance = np.clip(self.K_dd * speed, 8, 20)

        track_point = get_target_point(look_ahead_distance, waypoints)
        if track_point is None:
            raise RuntimeError

        alpha = np.arctan2(track_point[1], track_point[0])

        # Change the steer output with the lateral controller.
        steer = np.arctan((2 * self.wheel_base * np.sin(alpha)) / look_ahead_distance)

        return steer


class PIDController:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.int_term = 0
        self.derivative_term = 0
        self.last_error = None

    def get_control(self, target, measurement, dt):
        error = target - measurement
        self.int_term += error * self.Ki * dt
        if self.last_error is not None:
            self.derivative_term = (error - self.last_error) / dt * self.Kd
        self.last_error = error
        return self.Kp * error + self.int_term + self.derivative_term


class PurePursuitController:
    def __init__(
        self,
        pure_pursuit=None,
        pid=None,
    ):
        if pure_pursuit is None:
            self.pure_pursuit = PurePursuit()
        else:
            self.pure_pursuit = pure_pursuit
        if pid is None:
            self.pid = PIDController(Kp=0.20, Ki=0.01, Kd=0)
        else:
            self.pid = pid

    def get_control(self, actor, waypoints, target_speed, dt):

        p = actor.get_transform().location
        r = actor.get_transform().rotation
        v = actor.get_velocity()
        current_speed = math.hypot(v.x, v.y, v.z)  # meters per second

        # We will make calculations wrt actor frame
        theta = np.radians(r.yaw)
        c, s = np.cos(theta), np.sin(theta)
        R = np.array(((c, -s), (s, c)))  # Rotation matrix

        # Translate absolute waypoints to actor's frame  filter
        # And discard waypoints behind the actor
        relative_points = [np.array([0, 0])]
        for wp in waypoints:
            point = np.matmul(np.array([wp.x - p.x, wp.y - p.y]), R)
            if point[0] > 0:
                relative_points.append(point)

        accel = self.pid.get_control(target_speed, current_speed, dt)
        steer = self.pure_pursuit.get_control(relative_points, current_speed)

        return accel, steer

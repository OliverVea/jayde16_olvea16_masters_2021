from primitives import Pose

class Graph:
    def __init__(self, initial_pose: Pose = Pose(0, 0, 0)):
        self.landmarks = []
        self.poses = [initial_pose]

        self.landmark_constraints = []
        self.odometry_constraints = []

    def add_odometry(self, odometry_constraint: Pose):
        new_pose = self.poses[-1]

        new_pose = odometry_constraint.absolute(new_pose) # The actual calculation. The rest are fun too, though.
        #new_pose = new_pose.absolute(odometry_constraint)
        #new_pose = odometry_constraint.relative(new_pose)
        #new_pose = new_pose.relative(odometry_constraint)

        self.poses.append(new_pose)
        self.odometry_constraints.append(odometry_constraint)
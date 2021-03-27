class Landmark:
    def __init__(self, pose):
        self.poses = [pose]

    def add_pose(self, pose):
        self.poses += [pose]

    def get_pose(self):
        return Point([pose.x for pose in poses]/len(self.poses),  )
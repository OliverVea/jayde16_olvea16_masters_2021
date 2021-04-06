from robsim.primitives import Point, Pose
from robsim.utility import dist_l2

import matplotlib.pyplot as plt

from scipy.optimize import least_squares
import scipy.sparse as sparse

import numpy as np

from math import pi

class Slam:

    def __init__(self, origin, n_landmarks, cov_odometry, cov_landmarks):
        self.origin = origin
        self.n_landmarks = n_landmarks
        self.landmarks = [Point(0, 0) for _ in range(n_landmarks)]
        self.landmark_initialized = [False for _ in range(n_landmarks)]
        self.route = [origin]

        self.cov_odometry = cov_odometry
        self.cov_landmarks = cov_landmarks

                                       #    v Transformation from origin to first position in graph.
        self.odometry_constraints = [] # [(T_A, O_A), (T_AB, O_AB), (T_BC, O_BC)] <- O_ij is the information matrix of contstaint (i,j).
        self.landmark_constraints = [] # [{0: (T_A1, O_A1), 1: (T_A2, O_A2)}, {1: (T_B2, O_B2)}, {1: (T_C2, O_C2), 2: (T_C3, O_C3)}]

    @staticmethod
    def _get_state(route, landmarks):
        for i, point in enumerate(landmarks):
            if point == None:
                landmarks[i] = Point(0, 0) # Insert valid value if not measured yet.
                                                                                        #             [route, landmarks]
        state = [(p.x, p.y, p.theta) for p in route] + [(p.x, p.y) for p in landmarks]  #    [r1, r2, ..., rm-1, l1, l2, ..., ln-1]
        state = [val for t in state for val in t]                                       # [r1x, r1y, r1t, r2x, ..., l1x, l1y, l2x, ...]

        return state

    @staticmethod
    def _from_state(state, n_landmarks): 
        n_route = (len(state) - n_landmarks * 2) // 3
        n = n_route + n_landmarks

        route = state[:n_route*3]
        route = [(route[i*3], route[i*3+1], route[i*3+2]) for i in range(n_route)]
        route = [Pose(*pose) for pose in route]

        
        landmarks = state[n_route*3:]
        landmarks = [(landmarks[i*2], landmarks[i*2+1]) for i in range(n_landmarks)]
        landmarks = [Point(*pose) for pose in landmarks]

        return route, landmarks

    @staticmethod
    def _error(state, origin, n_landmarks, odometry_constraints, landmark_constraints, var_odometry, var_landmarks):
        state[:3] = np.array([origin.x, origin.y, origin.theta])
        
        route, landmarks = Slam._from_state(state, n_landmarks)

        n_route = len(route)

        odometry_errors = []
        for a, b, constraint in zip(route[:-1], route[1:], odometry_constraints):
            b_ = constraint.absolute(a)
            #error = dist_l2(b, b_) * var_odometry
            error = b - b_

            odometry_errors.append(error.x * var_odometry)
            odometry_errors.append(error.y * var_odometry)
            odometry_errors.append(error.theta * var_odometry / (2 * pi))

        landmark_errors = []
        for origin, constraints in zip(route[1:], landmark_constraints):
            for landmark in constraints:
                point = landmarks[landmark]
                point_ = constraints[landmark].absolute(origin)

                #error = dist_l2(point, point_) * var_landmarks
                error = point - point_

                landmark_errors.append(error.x * var_landmarks)
                landmark_errors.append(error.y * var_landmarks)

        errors = odometry_errors + landmark_errors

        return errors

    def get_sparsity(self):
        n = len(self.route) * 3 + len(self.landmarks) * 2

        sparsity = []
        
        for i in range(len(self.route) - 1):
            row = np.zeros((n,))

            row[i*3:(i*3+6)] = [1, 1, 1, 1, 1, 1]

            for _ in range(3):
                sparsity.append(row)

        for i, constraints in enumerate(self.landmark_constraints):
            for landmark in constraints:
                row = np.zeros((n,))

                row[i*3+3:i*3+6] = [1, 1, 1]

                offset = len(self.route) * 3
                j = offset + landmark * 2
                
                row[j:j+2] = [1, 1]

                for _ in range(2):
                    sparsity.append(row)

        sparsity = np.array(sparsity)

        return sparsity

    def optimize(self):
        fun = Slam._error
        state = self._get_state(self.route, [pt for pt in self.landmarks])

        result = least_squares(fun, state, 
            args=(self.origin, self.n_landmarks, self.odometry_constraints, \
                self.landmark_constraints, 1, 100),
            verbose=0,
            ftol=1e-5,
            xtol=1e-5,
            gtol=1e-5,
            jac='3-point',
            loss='huber',
            #jac_sparsity=self.get_sparsity()
        )

        self.route, self.landmarks = Slam._from_state(result.x, self.n_landmarks)

    def add_constraints(self, odometry_constraint, landmark_contraints):
        self.odometry_constraints.append(odometry_constraint)

        landmark_contraints_dict = {}
        for landmark, measurement in landmark_contraints:
            landmark_contraints_dict[landmark] = measurement

        self.landmark_constraints.append(landmark_contraints_dict)

        # Add pose just from odometry
        new_pose = self.route[-1]
        new_pose = odometry_constraint.absolute(new_pose)
        self.route.append(new_pose)

        # Add landmark position if first measurement
        for landmark, measurement in landmark_contraints:
            if not self.landmark_initialized[landmark]:
                self.landmarks[landmark] = measurement.absolute(new_pose)
                self.landmark_initialized[landmark] = True

    def plot(self, plot_landmark_measurements: bool = False):
        fig = plt.figure()

        plt.plot([p.x for p in self.route], [p.y for p in self.route], '-x')
        
        lms = [p for p in self.landmarks if p != None]
        plt.plot([p.x for p in lms], [p.y for p in lms], 'o', color='red')

        if plot_landmark_measurements:
            for pose, measurements in zip(self.route, self.landmark_constraints):
                for landmark in measurements:
                    plt.plot(
                        (pose.x, self.landmarks[landmark].x), 
                        (pose.y, self.landmarks[landmark].y), 
                        '--', color='black')

        ax = plt.gca()
        ax.set_aspect(1)
        
        return fig
        
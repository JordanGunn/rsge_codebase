import numpy as np
from scipy.stats import kstest
from dataclasses import dataclass
from collections import namedtuple

# -----------------------------------------------------------
# -- Type definitions
# -----------------------------------------------------------
Point3D = namedtuple("Point", "x y z")
PointsXYZA = namedtuple("PointsXYZA", "x y z a")
Eigen = namedtuple("Eigen", "values vectors")
KolmogorovSmirnov = namedtuple("KolmogorovSmirnov", "p statistic")


# -----------------------------------------------------------
# -- Data class definitions
# -----------------------------------------------------------
@dataclass
class MeasurementQualityIndicator:
    """
    Provides a container, as well as type restriction for storage of Quality Indicator
    parameters of derived surfaces.
    """

    angle_reflectance: float
    rmse: float


@dataclass
class MeasurementQualityLevel:
    """
    Provides a container, as well as type restriction for storage of quality levels of
    derived surfaces.
    """

    QL1: MeasurementQualityIndicator
    QL2: MeasurementQualityIndicator
    QL3: MeasurementQualityIndicator
    QLWARN: MeasurementQualityIndicator
    QLERROR: MeasurementQualityIndicator


# ------------------------------------------------------
# -- Constants
# ------------------------------------------------------

# Quality Level Constants
QL1 = 1
QL2 = 2
QL3 = 3
QLWARN = 4
QLERROR = 5

# Defines quality indicators for angles and surfaces
MEASUREMENT_QUALITY = MeasurementQualityLevel(
    QL1=MeasurementQualityIndicator(5.0, 0.020),        # 1dRMS
    QL2=MeasurementQualityIndicator(15.0, 0.040),       # 2dRMS
    QL3=MeasurementQualityIndicator(30.0, 0.060),       # 3dRMS
    QLWARN=MeasurementQualityIndicator(45.0, 0.200),
    QLERROR=MeasurementQualityIndicator(90.0, 0.300)
)


class LidarSurface:

    def __init__(self, points: PointsXYZA, scan_angles: np.array = None):

        if self.__points_have_xyz(points):
            self.surface_distances = None
            self.points = np.vstack((points.x, points.y, points.z)).T
            self.point_count = self.points.size
            self.density = self.__surface_density()
            self.centroid = np.mean(self.points, axis=0)
            self.covariance = np.cov((self.points - self.centroid).T)
            self.eigen = self.__compute_eigen()
            self.surface_normal = self.eigen.vectors[:, 0]
            self.curvature = self.__compute_curvature()
            self.plane = self.__compute_plane()
            self.rmse = self.__rmse()
            self.normality_deviation = self.set_deviation_angles(scan_angles) if scan_angles.size > 0 else None
            self.quality_level = self.__set_quality_level()
            self.ks_test = self.__ks_test()

    def __compute_curvature(self):
        # eigenvalues are in increasing order
        lambda1, lambda2, lambda3 = self.eigen.values
        curvature = (lambda1 / (lambda1 + lambda2 + lambda3))
        return curvature

    def __compute_plane(self):

        """
        Compute derived plane from input points.

        :return:
        """

        dot_product = -np.dot(self.surface_normal, self.centroid)
        plane = np.array(
            [
                self.surface_normal[0], self.surface_normal[1],
                self.surface_normal[2], dot_product
            ]
        )
        return plane

    def __rmse(self) -> float:
        """
        Computes the root mean squared error of the surface points from the surface plane.
        :return: Root mean squared error value.
        """
        # Compute the signed perpendicular distances of the points to the plane
        self.surface_distances = np.abs(np.dot(self.points - self.centroid, self.surface_normal))

        # Compute the RMSE
        rmse = np.sqrt(np.mean(np.square(self.surface_distances)))

        return rmse

    def __ks_test(self, distribution='norm'):
        """
        Performs a Kolmogorov-Smirnov test on the surface distances.

        Args:
            distribution (str): The name of the theoretical distribution to compare against.
                                Defaults to 'norm' (normal distribution).

        Returns:
            ks_statistic (float): The K-S statistic.
            p_value (float): The p-value resulting from the K-S test.
        """
        # Perform the K-S test
        ks_statistic = -1
        p_value = -1
        if self.surface_distances is not None:
            ks_statistic, p_value = kstest(self.surface_distances, distribution)

        return KolmogorovSmirnov(p_value, ks_statistic)

    def __compute_eigen(self):

        """
        Compute the eigenvalues and eigenvectors for the surface.

        :return:
        """

        eigenvalues, eigenvectors = np.linalg.eigh(self.covariance)
        return Eigen(eigenvalues, eigenvectors)

    def set_deviation_angles(self, scan_angles: np.array) -> np.array:

        """
        Compute the angle between derived surface normal and all surface points.

        :param scan_angles: Array or scan angles for surface points.
        :return: Deviation angles as numpy array.
        """

        rads = np.deg2rad(scan_angles - 180)
        unit_vectors = np.array([np.cos(rads), np.sin(rads), np.zeros_like(rads)]).T
        dot_products = np.dot(unit_vectors, self.surface_normal)

        return np.rad2deg(np.arccos(dot_products))

    def __surface_density(self) -> float:

        """
        Compute the point density of the area selected for surface derivation.

        :return:
        """

        # extract x, y, and z coordinates into separate arrays
        x = self.points[:, 0]
        y = self.points[:, 1]
        x_min, x_max = np.min(x), np.max(x)
        y_min, y_max = np.min(y), np.max(y)
        dim_x = x_max - x_min
        dim_y = y_max - y_min
        density = self.point_count / (dim_x * dim_y)
        return density

    @staticmethod
    def __points_have_xyz(points: PointsXYZA):

        """
        Determine that input points have coordinates in 3-Dimensions.

        :param points:
        :return:
        """

        return points.x.size > 0 and points.y.size > 0 and points.z.size > 0

    def __set_quality_level(self):

        """
        Compute the quality level indicator of the derived surface.

        :return:
        """

        quality_level = QLERROR
        if self.__is_QL1():
            quality_level = QL1
        if self.__is_QL2():
            quality_level = QL2
        if self.__is_QL3():
            quality_level = QL3
        if self.__is_QLWARN():
            quality_level = QLWARN
        if self.__is_QLERROR():
            quality_level = QLERROR

        return quality_level

    def __is_QL1(self):
        return self.rmse <= MEASUREMENT_QUALITY.QL1.rmse

    def __is_QL2(self):
        lower_bound = self.rmse > MEASUREMENT_QUALITY.QL1.rmse
        upper_bound = self.rmse <= MEASUREMENT_QUALITY.QL2.rmse
        return lower_bound and upper_bound

    def __is_QL3(self):
        lower_bound = self.rmse > MEASUREMENT_QUALITY.QL2.rmse
        upper_bound = self.rmse <= MEASUREMENT_QUALITY.QL3.rmse
        return lower_bound and upper_bound

    def __is_QLWARN(self):
        lower_bound = self.rmse > MEASUREMENT_QUALITY.QL2.rmse
        upper_bound = self.rmse <= MEASUREMENT_QUALITY.QLWARN.rmse
        return lower_bound and upper_bound

    def __is_QLERROR(self):
        lower_bound = self.rmse > MEASUREMENT_QUALITY.QLWARN.rmse
        upper_bound = self.rmse <= MEASUREMENT_QUALITY.QLERROR.rmse
        return lower_bound and upper_bound


class Not3DDataError(Exception):

    def __init__(self, message: str = "Does not contain XYZ Coordinates."):
        self.message = message
        super().__init__(self.message)
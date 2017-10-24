# coding=utf-8
"""
Utility files for splitting large images into subimages

Author: Tom Doel
Copyright UCL 2017

"""


class SubImage(object):
    """An image which forms part of a larger image"""

    def __init__(self, descriptor, data_source):
        self._descriptor = descriptor
        self._data_source = data_source

        # Construct the origin offset used to convert from global
        # coordinates. This excludes overlapping voxels
        self._image_size = self._descriptor.image_size
        self._origin_start = self._descriptor.origin_start
        self._origin_end = self._descriptor.origin_end
        self._roi_start = self._descriptor.roi_start
        self._roi_end = self._descriptor.roi_end
        self._ranges = self._descriptor.ranges

    def get_ranges(self):
        """Returns the full range of global coordinates covered by this
        subimage """

        return self._ranges

    def write_image_stream(self, start_coords, image_line):
        """Writes a line of image data to a binary file at the specified
        image location """

        start_coords_local = self._convert_coords_to_local(start_coords)
        self._data_source.write_image_stream(start_coords_local, image_line)

    def read_image_stream(self, start_coords, num_voxels_to_read):
        """Reads a line of image data from a binary file at the specified
        image location """

        if not self.contains_voxel(start_coords, True):
            raise ValueError('The data range to load extends beyond this file')

        # Don't read bytes beyond the end of the valid range
        if start_coords[0] + num_voxels_to_read - 1 > self._roi_end[0]:
            num_voxels_to_read = self._roi_end[0] - start_coords[0] + 1

        start_coords_local = self._convert_coords_to_local(start_coords)
        return self._data_source.read_image_stream(start_coords_local,
                                                   num_voxels_to_read)

    def contains_voxel(self, start_coords_global, must_be_in_roi):
        """Determines if the specified voxel lies within the ROI of this
        subimage """

        if must_be_in_roi:
            return (
                self._roi_start[0] <= start_coords_global[0] <= self._roi_end[
                    0] and
                self._roi_start[1] <= start_coords_global[1] <= self._roi_end[
                    1] and
                self._roi_start[2] <= start_coords_global[2] <= self._roi_end[
                    2])

        return (
            self._origin_start[0] <= start_coords_global[0] <=
            self._origin_end[
                0] and
            self._origin_start[1] <= start_coords_global[1] <=
            self._origin_end[
                1] and
            self._origin_start[2] <= start_coords_global[2] <=
            self._origin_end[
                2])

    def close(self):
        """Close all streams and files"""
        self._data_source.close()

    def get_bytes_per_voxel(self):
        """Return the number of bytes used to represent a single voxel"""
        return self._data_source.get_bytes_per_voxel()

    def _convert_coords_to_local(self, start_coords):
        return [start_coord - origin_coord for start_coord, origin_coord in
                zip(start_coords, self._origin_start)]

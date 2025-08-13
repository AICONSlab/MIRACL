from enum import Enum


class CliGroup(Enum):
    SEGMENTATION = ("segmentation", "Args related to segmentation processing")
    REGISTRATION = ("registration", "Args for image registration")
    CONV_TIFF_NII = ("conversion", "Args for image conversion from tiff to nifti")
    SKELETONIZATION = ("skeletonization", "Args for skeletonization tasks")
    REQUIRED = ("required", "required arguments")

    @property
    def description(self):
        return self.value[1]

    @property
    def label(self):
        return self.value[0]


# group_name = obj.cli_group  # instance of CliGroup
# parser.add_argument_group(title=group_name.label, description=group_name.description)

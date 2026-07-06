from typing import Literal, TypeAlias

KeypointType: TypeAlias = Literal["face_5pt"] | str
"""
A keypoint layout identifier.

User-defined keypoint types are accepted as plain strings.

- face_5pt: 5 facial points ordered by image position to match the
  ArcFace / SCRFD template (index0 = the eye on the image-left side):
  1. left eye (image-left side)
  2. right eye (image-right side)
  3. nose
  4. left mouth corner (image-left side)
  5. right mouth corner (image-right side)
  Note: "left"/"right" here are image-space sides, not the subject's
  anatomical sides (the subject's left eye appears on the image-right).
"""

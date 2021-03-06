"""
Collection of higher level functions using low level pymiere code
"""
import pymiere

# premiere uses ticks as its base time unit, this is used to convert from ticks to seconds
TICKS_PER_SECONDS = 254016000000


def check_active_sequence(crash=True):
    """
    Check if a project is opened and if a sequence is active

    :param crash: (bool) crash or return status as bool
    :return: (bool), (bool) project is opened, sequence is active
    """
    # is there a project opened ?
    if not pymiere.objects.app.isDocumentOpen():
        msg = "No project is opened"
        if crash:
            raise IOError(msg)
        print(msg)
        return False, False
    # is there a sequence opened ?
    if not pymiere.objects.app.project.activeSequence:
        msg = "No sequence is currently opened in the UI"
        if crash:
            raise AttributeError(msg)
        print(msg)
        return True, False
    return True, True


def get_item_recursive(item, add_root=False, filter_function=lambda i: True):
    """
    Recursively browse the project items returning a list of item with associated filepaths

    :param item: (ProjectItem) start item to browse from
    :param add_root: (bool) add the root (first given item) to the list and to the path
    :param filter_function: (None or func) function applied on all item, should return a bool adding or dismissing it
    :return: (list of ProjectItem)
    """
    all_children = [item] if filter_function(item) and add_root else list()
    # no children under item
    if item.children is None:
        return all_children
    # iter over children
    for c in item.children:
        all_children.extend(get_item_recursive(c, add_root=True, filter_function=filter_function))
    return all_children


def list_sequences():
    """
    List available sequence sin the opened project, print infos and return objects

    :return: (list of Sequence) all sequences available in the project
    """
    sequences = pymiere.objects.app.project.sequences
    print("Found {} sequences in project '{}'\n".format(len(sequences), pymiere.objects.app.project.name))
    for sequence in sequences:
        print("Name : '{}'\nPath : '{}'".format(sequence.name, sequence.projectItem.treePath))
        print("Sequence setting :")
        settings = sequence.getSettings()
        for setting in ["videoFrameRate", "videoFrameWidth", "videoFrameHeight", "videoPixelAspectRatio", "audioSampleRate"]:
            value = settings.__getattribute__(setting)
            if isinstance(value, pymiere.Time):
                value = 1/value.seconds
            print("\t{} : {}".format(setting, value))
        print("\n")
    return sequences


def list_video(sequence):
    """
    List all video clips on all tracks on this sequence

    :param sequence: (Sequence)
    :return: (list of Clip)
    """
    video_clips = list()
    tracks = sequence.videoTracks
    for track in tracks:
        print("Track :", track.name or track.id)  # Premiere 2017 doesn't have 'name' property on tracks
        clips = track.clips
        for clip in clips:
            print("name", clip.name)  # Premiere 2017 doesn't have 'name' property on clips
            print("path", clip.projectItem.getMediaPath())
            print("duration", clip.duration.seconds)
            print("start", clip.start.seconds)
            print("in", clip.inPoint.seconds)
            print("out", clip.outPoint.seconds)
            print("end", clip.end.seconds)
            print("")
            video_clips.append(clip)
    return video_clips


def edit_clip(clip, start_on_timeline, end_on_timeline, in_point_on_clip, out_point_on_clip, fps=None):
    """
    Trim or move clip. This in not available in ppro 2017, use insertClip or overwriteClip

    :param clip: (Clip)
    :param start_on_timeline: (int) Frame at which the clip should start in the sequence timeline
    :param end_on_timeline: (int) Frame at which the clip should end in the sequence timeline
    :param in_point_on_clip: (int) First frame we will see of the clip (in the clip own timeline)
    :param out_point_on_clip: (int) Last frame we will see of the clip (in the clip own timeline)
    :param out_point_on_clip: (int) Last frame we will see of the clip (in the clip own timeline)
    """
    # get clip fps if no fps given
    if fps is None:
        fps = clip.projectItem.getFootageInterpretation().frameRate  # not available in ppro 2017, use sequence.timebase
    # check length match
    if end_on_timeline - start_on_timeline != out_point_on_clip - in_point_on_clip:
        raise ValueError("Duration in timeline ({} frames) doesn't match duration of clip ({} frames)".format(end_on_timeline - start_on_timeline, out_point_on_clip - in_point_on_clip))
    # convert frame to seconds and generate Time objects (note that to properly construct a Time object we should first
    # init the object empty, then set the seconds property. Don't set the ticks property, set the seconds and the ticks
    # will be properly set, the inverse is not True
    start = pymiere.Time()
    start.seconds = start_on_timeline / fps
    end = pymiere.Time()
    end.seconds = end_on_timeline / fps
    in_point = pymiere.Time()
    in_point.seconds = in_point_on_clip / fps
    out_point = pymiere.Time()
    out_point.seconds = out_point_on_clip / fps
    clip.end = end
    clip.start = start
    clip.inPoint = in_point
    clip.outPoint = out_point


if __name__ == "__main__":
    pass

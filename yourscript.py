import re
import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class ROI:
    xmin: int
    xmax: int
    ymin: int
    ymax: int


def _run(tool, *args):
    if shutil.which(tool) is None:
        raise FileNotFoundError(
            f"'{tool}' not found on PATH. Make sure the slsDetectorPackage "
            "binaries are installed and in your PATH."
        )
    result = subprocess.run([tool, *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"{tool} {' '.join(args)} failed:\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout.strip()


def get_rx_roi(det_id=-1):
    """Return receiver ROI(s) as a list of ROI objects."""
    cmd = "rx_roi" if det_id == -1 else f"{det_id}:rx_roi"
    out = _run("sls_detector_get", cmd)
    print("raw output:", out)  # useful to check the format on your version

    # Drop the leading command name, then grab every integer in the response.
    body = out.split(None, 1)[1] if " " in out else ""
    nums = [int(n) for n in re.findall(r"-?\d+", body)]
    if len(nums) % 4 != 0:
        raise ValueError(f"Could not parse ROI from output: {out!r}")
    return [ROI(*nums[i:i + 4]) for i in range(0, len(nums), 4)]


def set_rx_roi(rois, det_id=-1):
    """Set receiver ROI. Accepts a single ROI or a list of ROI objects."""
    if isinstance(rois, ROI):
        rois = [rois]
    cmd = "rx_roi" if det_id == -1 else f"{det_id}:rx_roi"
    for roi in rois:
        _run(
            "sls_detector_put",
            cmd,
            str(roi.xmin), str(roi.xmax), str(roi.ymin), str(roi.ymax),
        )


def clear_rx_roi(det_id=-1):
    cmd = "rx_clearroi" if det_id == -1 else f"{det_id}:rx_clearroi"
    _run("sls_detector_put", cmd)


if __name__ == "__main__":
    print(get_rx_roi())
    set_rx_roi(ROI(xmin=0, xmax=255, ymin=0, ymax=255))
    print(get_rx_roi())
    # clear_rx_roi()

# dials.estimate_pedestal by Takanori Nakane
#
# Based on DIALS' src/dials/command_line/estimate_gain.py.
# Thus, this inherits its BSD license:
# https://github.com/dials/dials/blob/main/LICENSE.

import pickle

import iotbx.phil
from scitbx.array_family import flex

from dials.util import Sorry, show_mail_handle_errors
from dials.util.options import ArgumentParser, flatten_experiments

import numpy as np

help_message = """

This program can be used to estimate the peedstal of the detector.

Examples::

  dials.estimate_pedestal imported.expt
"""

phil_scope = iotbx.phil.parse(
    """\
  rms_cutoff = 5
    .type = float
""",
    process_includes=True,
)


def estimate_pedestal(imageset, rms_limit = 5):
    for image_no in range(len(imageset)):
        raw_data = np.array(imageset.get_raw_data(image_no))
        min = np.min(raw_data)
        median = np.median(raw_data)
        rms = np.sqrt(np.mean((raw_data - median) ** 2))

        filtered = raw_data[np.abs(raw_data - median) < rms_limit * rms]
        filtered_rms = np.sqrt(np.mean((filtered - median) ** 2))

        below5 = np.sum(raw_data < median - 5 * filtered_rms)
        below3 = np.sum(raw_data < median - 3 * filtered_rms)

        print(f"min, median, rms, filtered_rms, #<-5RMS, #<-3RMS: {min:6.1f}, {median:6.2f}, {rms:5.2f}, {filtered_rms:5.2f}, {below5: 6d}, {below3: 6d}")

    #return pedestal

@show_mail_handle_errors()
def run(args=None):
    usage = "dials.estimate_pedestal [options] imported.expt"

    parser = ArgumentParser(
        usage=usage,
        phil=phil_scope,
        read_experiments=True,
        check_format=True,
        read_experiments_from_images=True,
        epilog=help_message,
    )

    params, options = parser.parse_args(args, show_diff_phil=False)

    # Log the diff phil
    diff_phil = parser.diff_phil.as_str()
    if diff_phil != "":
        print("The following parameters have been modified:\n")
        print(diff_phil)

    experiments = flatten_experiments(params.input.experiments)

    if len(experiments) == 0:
        parser.print_help()
        return
    elif len(experiments) > 1:
        raise Sorry("Only one experiment can be processed at a time")
    else:
        imagesets = experiments.imagesets()

    assert len(imagesets) == 1
    imageset = imagesets[0]
    estimate_pedestal(imageset, params.rms_cutoff)
    # Update experiment and write it?

if __name__ == "__main__":
    run()

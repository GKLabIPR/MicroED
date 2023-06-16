# Based on Graeme Winter's code at
# https://github.com/dials/dials/pull/2232,
# Takanori Nakane (hopefully) fixed frame indexing bugs.
#
# Same license as DIALS (https://github.com/dials/dials/blob/main/LICENSE). 

from __future__ import annotations

import logging
import sys
from array import array
from itertools import groupby

import libtbx.phil
from dxtbx.model.experiment_list import ExperimentList

from dials.array_family import flex
from dials.util import detect_blanks, show_mail_handle_errors

logger = logging.getLogger("dials.filter_blanks")

phil_scope = libtbx.phil.parse(
    """\
phi_step = 2
  .type = float(value_min=0)
  .help = "Width of bins in degrees."
counts_fractional_loss = 0.1
  .type = float(value_min=0, value_max=1)
  .help = "Fractional loss (relative to the bin with the most counts) after "
          "which a bin is flagged as potentially containing blank images."
misigma_fractional_loss = 0.1
  .type = float(value_min=0, value_max=1)
  .help = "Fractional loss (relative to the bin with the highest misigma) after "
          "which a bin is flagged as potentially containing blank images."
output {
  experiments = not_blank.expt
    .type = path
    .help = "Experiments with blank frames removed"
  reflections = not_blank.refl
    .type = path
    .help = "Corresponding non-blank reflection lists"
}
""",
    process_includes=True,
)


help_message = "dials.filter_blanks [options] imported.expt strong.refl"


def array_to_valid_ranges(a):
    """Return ranges where a[j] is truthy"""
    # Takanori modified this to return the longest range
    start = 0
    best = 0
    result = None
    for k, g in groupby(a):
        l = list(g)
        n = len(l)
        if k and n > best:
            result = [(start, start + n)]
            best = n
        start += n

    return result


@show_mail_handle_errors()
def run(args=None):
    from dials.util import log
    from dials.util.options import (
        ArgumentParser,
        reflections_and_experiments_from_files,
    )

    usage = help_message

    parser = ArgumentParser(
        usage=usage,
        phil=phil_scope,
        read_experiments=True,
        read_reflections=True,
        check_format=False,
        epilog=help_message,
    )

    params, _ = parser.parse_args(args)
    reflections, experiments = reflections_and_experiments_from_files(
        params.input.reflections, params.input.experiments
    )

    if len(experiments) == 0 or len(reflections) == 0:
        parser.print_help()
        exit(0)

    # Configure the logging
    log.config(logfile="dials.filter_blanks.log")

    # Log the diff phil
    diff_phil = parser.diff_phil.as_str()
    if diff_phil != "":
        logger.info("The following parameters have been modified:\n")
        logger.info(diff_phil)

    # TODO make this work gracefully if multiple reflection lists /
    # experiment files are passed in (rather than just the multi-run
    # single-file equivalent)
    reflections = reflections[0].split_by_experiment_id()

    assert len(reflections) == len(experiments)

    if any(experiment.is_still() for experiment in experiments):
        sys.exit("dials.detect_blanks can only be used with rotation data")

    valid_experiments = ExperimentList()
    valid_reflections = flex.reflection_table()

    for expt, refl in zip(experiments, reflections):
        imageset = expt.imageset
        scan = imageset.get_scan()

        # See https://github.com/dials/dials/pull/2232#issuecomment-1335063098
        valid = array("b", [0 for _ in range(scan.get_array_range()[1] + 1)])

        for i in range(*scan.get_array_range()):
            valid[i] = 1
        integrated_sel = refl.get_flags(refl.flags.integrated)
        indexed_sel = refl.get_flags(refl.flags.indexed)
        centroid_outlier_sel = refl.get_flags(refl.flags.centroid_outlier)
        strong_sel = refl.get_flags(refl.flags.strong)
        indexed_sel &= ~centroid_outlier_sel

        logger.info(f"Analysis of {strong_sel.count(True)} strong reflections:")
        strong_results = detect_blanks.blank_counts_analysis(
            refl.select(strong_sel),
            scan,
            phi_step=params.phi_step,
            fractional_loss=params.counts_fractional_loss,
        )
        for blank_start, blank_end in strong_results["blank_regions"]:
            logger.info(f"Potential blank images: {blank_start + 1} -> {blank_end}")
            for j in range(blank_start, blank_end):
                valid[j] = 0

        indexed_results = None
        if indexed_sel.count(True) > 0:
            logger.info(f"Analysis of {indexed_sel.count(True)} indexed reflections:")
            indexed_results = detect_blanks.blank_counts_analysis(
                refl.select(indexed_sel),
                scan,
                phi_step=params.phi_step,
                fractional_loss=params.counts_fractional_loss,
            )
            for blank_start, blank_end in indexed_results["blank_regions"]:
                logger.info(f"Potential blank images: {blank_start + 1} -> {blank_end}")
                for j in range(blank_start, blank_end):
                    valid[j] = 0

        integrated_results = None
        if integrated_sel.count(True) > 0:
            logger.info(
                f"Analysis of {integrated_sel.count(True)} integrated reflections:"
            )
            integrated_results = detect_blanks.blank_integrated_analysis(
                refl.select(integrated_sel),
                scan,
                phi_step=params.phi_step,
                fractional_loss=params.misigma_fractional_loss,
            )
            for blank_start, blank_end in integrated_results["blank_regions"]:
                logger.info(f"Potential blank images: {blank_start + 1} -> {blank_end}")
                for j in range(blank_start, blank_end):
                    valid[j] = 0

        valid_ranges = array_to_valid_ranges(valid)

        if not valid_ranges:
            continue

        start, end = valid_ranges[0]
        offset = scan.get_array_range()[0]
        # See https://github.com/dials/dials/pull/2232#issuecomment-1337381532 
        print([start, end, offset])
        expt.scan = expt.scan[(start-offset):(end-offset)]
        valid_experiments.append(expt)
        z = refl["xyzobs.px.value"].parts()[2]
        keep = (z >= start) & (z < end)
        valid_reflections.extend(refl.select(keep))

    if params.output.reflections:
        valid_reflections.as_file(params.output.reflections)
    if params.output.experiments:
        valid_experiments.as_file(params.output.experiments)


if __name__ == "__main__":
    run()

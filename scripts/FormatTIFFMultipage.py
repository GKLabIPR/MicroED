"""A format class for generic multi-page TIFF images plus implementations for specific
detectors producing electron diffraction data"""

# By Takanori Nakane, Osaka University
#
# This is based on dxtbx (https://github.com/dials/dxtbx) by the DIALS project
# and FormatTIFFgeneric.py by David Waterman
#  (https://github.com/dials/dxtbx_ED_formats/blob/master/FormatTIFFgeneric.py)
# and inherits its license (BSD-3).

from dxtbx.format.Format import Format
from dxtbx.format.FormatMultiImage import FormatMultiImage
import numpy
from scitbx.array_family import flex
from dxtbx import flumpy

try:
    import tifffile # needs "conda install tifffile"
except ImportError:
    tifffile = None

# I cannot use FormatTIFFgeneric because it is for single page.
class FormatMultiPageTIFF(FormatMultiImage, Format):
    """An experimental image reading class for multiplage TIFF images
    """
    known_detectors = {(4096, 4096): 0.155, # TVIPS
                       (2048, 2048): 0.310, # TVIPS bin2
                       (4092, 5760): 0.005  # K3 counting
                      }

    def __init__(self, image_file, **kwargs):
        FormatMultiImage.__init__(self, **kwargs)
        Format.__init__(self, image_file, **kwargs)

    def _start(self):
        with tifffile.TiffFile(self._image_file) as tif:
            self._nframes = len(tif.pages)
            self._size = tif.pages[0].shape

    @staticmethod
    def understand(image_file):
        """Check to see if this looks like a square TIFF image with 4K or 2K pixels in each axis.
        WARNING: This picks up all TIFF images of this size!
        """

        try:
            with tifffile.TiffFile(image_file) as tif:
                page = tif.pages[0]
                if page.shape in FormatMultiPageTIFF.known_detectors:
                    return True
                else:
                    return False
        except:
            return False

    def get_raw_data(self, index):
        """Get the pixel intensities"""

        raw_data = tifffile.imread(self._image_file, key=index)
        # The next line is not necessary if you start processing from the TIFF files.
        # If you process the original MRC files and then convert them to TIFF by mrc2tif in the IMOD suite
        # for archiving, flipping the slow axis is necessary, since IMOD flips the axis upon conversion.
        raw_data = numpy.flip(raw_data, 0)
        return flumpy.from_numpy(raw_data.astype(float))

    def _goniometer(self):
        """Dummy goniometer, 'vertical' as the images are viewed. The handedness of the rotation
        must be confirmed for each scope."""

        return self._goniometer_factory.known_axis((0, -1, 0))

    def _beam(self):
        """Dummy beam, energy 300 keV"""

        wavelength = 0.019676 # use 0.02508 for 200 kV
        return self._beam_factory.make_polarized_beam(
            sample_to_source=(0.0, 0.0, 1.0),
            wavelength=wavelength,
            polarization=(0, 1, 0),
            polarization_fraction=0.5,
        )

    def _detector(self):
        """Dummy detector at 70 cm"""

        image_size = (self._size[1], self._size[0]) # (x, y) i.e. (fast, slow)
        pixel_size = (self.known_detectors[self._size], self.known_detectors[self._size])
        trusted_range = (-1, 65535) # I don't know!
        beam_centre = [(p * i) / 2 for p, i in zip(pixel_size, image_size)]

        d = self._detector_factory.simple(
            "PAD", 700, beam_centre, "+x", "-y", pixel_size, image_size, trusted_range
        )
        return d

    def get_num_images(self):
        return self._nframes

    def _scan(self):
        """Dummy scan for this image at 1 deg/frame"""

        exposure = 0
        oscillation = (0.0, 1.0)
        epochs = [0] * self._nframes
        return self._scan_factory.make_scan(
            (1, self._nframes), exposure, oscillation, epochs, deg=True
        )

if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:]:
        print(FormatMultiPageTIFF.understand(arg))

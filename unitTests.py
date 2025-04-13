#!/usr/bin/env python3

# Import standard modules ...
import math
import unittest

# Import my modules ...
import hml

# Define a test case ...
class MyTestCase(unittest.TestCase):
    """
    Test the module "hml"
    """

    # Define a test ...
    def test_findFractionOfPixelWithinCircle(self):
        """
        Test the function "hml.findFractionOfPixelWithinCircle()"
        """

        # Assert results ...
        self.assertAlmostEqual(
            hml.findFractionOfPixelWithinCircle(
                0.0,
                1.0,
                0.0,
                1.0,
                1.0,
            ),
            math.pi / 4.0,
            places = 1,
        )
        self.assertAlmostEqual(
            hml.findFractionOfPixelWithinCircle(
                0.0,
                1.0,
                0.0,
                1.0,
                1.0,
                ndiv = 1024,
            ),
            math.pi / 4.0,
            places = 3,
        )

        # Assert results ...
        self.assertAlmostEqual(
            hml.findFractionOfPixelWithinCircle(
                0.0,
                1.0,
                0.0,
                1.0,
                0.5,
                cx = 0.5,
                cy = 0.5,
            ),
            math.pi * pow(0.5, 2),
            places = 1,
        )
        self.assertAlmostEqual(
            hml.findFractionOfPixelWithinCircle(
                0.0,
                1.0,
                0.0,
                1.0,
                0.5,
                  cx = 0.5,
                  cy = 0.5,
                ndiv = 1024,
            ),
            math.pi * pow(0.5, 2),
            places = 3,
        )

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Run the tests ...
    unittest.main()

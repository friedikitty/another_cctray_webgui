#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test runner for CCTray Build Status Monitor
Run all unit tests
"""
import unittest
import sys

if __name__ == "__main__":
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = "."
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)

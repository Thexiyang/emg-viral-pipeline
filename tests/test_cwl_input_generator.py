#!/bin/env python3

import os
import unittest
import subprocess 

import bin.cwl_input as cwl_input

import yaml


class CwlGeneration(unittest.TestCase):

    def _get_path(self):
        return os.path.abspath(
            "/" + os.path.dirname(__file__)
            + "/cwl_input_generation")

    def test_cwl_generation(self):
        """Assert that the .yml generation works.
        """
        result_file = self._get_path() + "/input_generated_basic.yml"
        args = [
            "python", os.path.abspath(cwl_input.__file__),
            "-i", "dummy_fasta.fasta",
            "-f", "2.0",
            "-s", "dummy_virsorter_dir",
            "-d", "dummty_virfinder_model",
            "-a", "dummy_hmms_tsv",
            "-j", "dummy_hmmscan_db",
            "-n", "dummy_nbci_db",
            "-b", "dummy_img_db",
            "-p", "dummy_pprmeta_simg",
            "-o", result_file
        ]
        process = subprocess.run(args)

        assert process.returncode == 0

        with open(result_file, "r") as rf_handler, \
             open(self._get_path() + "/expected_basic.yml", "r") as e_handler:
            produced_yaml = yaml.load(rf_handler, Loader=yaml.FullLoader)
            expected_yaml = yaml.load(e_handler, Loader=yaml.FullLoader)

        # clean
        os.remove(result_file)

        assert produced_yaml == expected_yaml

    def test_cwl_generation_every_option(self):
        """Assert that the .yml generation works.
        With all the options and flags.
        """
        result_file = self._get_path() + "/input_generated_full.yml"
        args = [
            "python", os.path.abspath(cwl_input.__file__),
            "-i", "dummy_fasta_second.fasta",
            "-f", "0.7",
            "-s", "dummy_virsorter_dir",
            "-d", "dummty_virfinder_model",
            "-a", "dummy_hmms_tsv",
            "-j", "dummy_hmmscan_db",
            "-n", "dummy_nbci_db",
            "-b", "dummy_img_db",
            "-v", "true",
            "-m", "dummy_mashmap_ref",
            "-p", "dummy_pprmeta_simg",
            "-o", result_file
        ]
        process = subprocess.run(args)

        assert process.returncode == 0

        with open(result_file, "r") as rf_handler, \
             open(self._get_path() + "/expected_full.yml", "r") as e_handler:
            produced_yaml = yaml.load(rf_handler, Loader=yaml.FullLoader)
            expected_yaml = yaml.load(e_handler, Loader=yaml.FullLoader)

        # clean
        os.remove(result_file)

        assert produced_yaml == expected_yaml

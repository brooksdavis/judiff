#!/usr/bin/env python
# -
# Copyright (c) 2016 SRI International
# All rights reserved.
#
# This software was developed by SRI International and the University of
# Cambridge Computer Laboratory under DARPA/AFRL contract FA8750-10-C-0237
# ("CTSRD"), as part of the DARPA CRASH research programme.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
from __future__ import print_function
import sys
import xml.etree.ElementTree as ET

gold_status = {}


def usage():
    print("usage: " + sys.argv[0] + " <gold-file> <comp-file> <outfile>")
    exit(1)


def test_status(test):
    failure = testcase.find('failure')
    skipped = testcase.find('skipped')
    if failure is not None:
        return "failed"
    if skipped is not None:
        return "skipped"
    return "passed"


if len(sys.argv) != 4:
    usage()
goldfile = sys.argv[1]
testfile = sys.argv[2]
outfile = sys.argv[3]

goldtree = ET.parse(goldfile)
goldroot = goldtree.getroot()

for testcase in goldroot.findall('testcase'):
    name = testcase.attrib['classname'] + ":" + testcase.attrib['name']
    gold_status[name] = test_status(testcase)

testtree = ET.parse(testfile)
testroot = testtree.getroot()
judc = ET.SubElement(testroot, 'testcase', attrib={'classname': "judiff", 'name': "status"})
sys_out = ET.SubElement(judc, 'system-out')
sys_out.text = "Input files:\ngold: " + goldfile + "\ncompare: " + testfile + "\n"
sys_error = ET.SubElement(judc, 'system-err')
sys_error.text = "Identical tests removed:\n"
for testcase in testtree.findall('testcase'):
    name = testcase.attrib['classname'] + ":" + testcase.attrib['name']
    status = test_status(testcase)
    if not name in gold_status:
        continue
    elif status == gold_status[name]:
        testroot.remove(testcase)
        sys_error.text += "classname: " + testcase.attrib['classname'] + " "
        sys_error.text += "name: " + testcase.attrib['name'] + "\n"

testtree.write(outfile)

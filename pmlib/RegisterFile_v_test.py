#=========================================================================
# Register File Test
#=========================================================================

from pymtl import *
import pmlib

from RegisterFile import RegisterFile

from pymtl.verilator_sim import get_verilated

#-------------------------------------------------------------------------
# Test 1R1W Register File
#-------------------------------------------------------------------------
def test_regfile_1R1W( dump_vcd ):

  # Test vectors

  test_vectors = [
    # rd_addr0  rd_data0  wr_en  wr_addr  wr_data
    [       0,   0x0000,     0,       0,   0x0000 ],
    [       1,   0x0000,     0,       1,   0x0008 ],
    # Write followed by Read
    [       3,   0x0000,     1,       2,   0x0005 ],
    [       2,   0x0005,     0,       2,   0x0000 ],
    # Simultaneous Write and Read
    [       3,   0x0000,     1,       3,   0x0007 ],
    [       3,   0x0007,     1,       7,   0x0090 ],
    [       7,   0x0090,     1,       3,   0x0007 ],
    # Write to zero
    [       0,   0x0000,     1,       0,   0x0FFF ],
    [       0,   0x0FFF,     1,       4,   0x0FFF ],
    [       0,   0x0FFF,     0,       4,   0x0BBB ],
    [       0,   0x0FFF,     0,       4,   0x0FFF ],
    [       4,   0x0FFF,     0,       0,   0x0000 ],
  ]

  # Instantiate and elaborate the model

  model = get_verilated( RegisterFile( nbits=16, nregs=8, rd_ports=1 ) )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.rd_addr[0].value = test_vector[0]
    model.wr_en.value      = test_vector[2]
    model.wr_addr.value    = test_vector[3]
    model.wr_data.value    = test_vector[4]

  def tv_out( model, test_vector ):
    #if test_vector[3] != '?':
    assert model.rd_data[0].value == test_vector[1]

  # Run the test

  sim = pmlib.TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "plab2-test_regfile_1R1W.vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Test 2R1W Register File
#-------------------------------------------------------------------------
def test_regfile_2R1W( dump_vcd ):

  # Test vectors

  test_vectors = [
    # rd_addr0 rd_data0  rd_addr0 rd_data0  wr_en wr_addr wr_data
    [       0,  0x0000,        1,  0x0000,     0,      0,  0x0000 ],
    [       3,  0x0000,        4,  0x0000,     1,      4,  0x0005 ],
    [       3,  0x0000,        4,  0x0005,     1,      2,  0x0006 ],
    [       4,  0x0005,        2,  0x0006,     0,      3,  0x0007 ],
    [       4,  0x0005,        4,  0x0005,     0,      7,  0x0090 ],
    [       4,  0x0005,        7,  0x0000,     0,      7,  0x0090 ],
    [       4,  0x0005,        7,  0x0000,     1,      7,  0x0090 ],
    [       4,  0x0005,        7,  0x0090,     1,      7,  0x0090 ],
  ]

  # Instantiate and elaborate the model

  model = get_verilated( RegisterFile( nbits=16, nregs=8, rd_ports=2 ) )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.rd_addr[0].value = test_vector[0]
    model.rd_addr[1].value = test_vector[2]
    model.wr_en.value      = test_vector[4]
    model.wr_addr.value    = test_vector[5]
    model.wr_data.value    = test_vector[6]

  def tv_out( model, test_vector ):
    assert model.rd_data[0].value == test_vector[1]
    assert model.rd_data[1].value == test_vector[3]

  # Run the test

  sim = pmlib.TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "plab2-test_regfile_2R1W.vcd" )
  sim.run_test()

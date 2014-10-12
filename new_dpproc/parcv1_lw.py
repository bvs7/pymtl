#=========================================================================
# parcv1 lw tests
#=========================================================================

from new_pymtl import *

from new_pmlib.SparseMemoryImage import SparseMemoryImage

#---------------------------------------------------------------------------
# String based Assembly Tests
#---------------------------------------------------------------------------
# Directed string based assembly tests

# test_start string

test_start = """
  .text;
  .align  4;
  .global _test;
  .ent    _test;
  _test:
"""

# test_end string

test_end   = """
  .end    _test;
"""

# Test instructions with no data hazards

def lw_no_hazards():

  asm_str = \
    ( test_start +
  """
      la    $2, tdata_0
      nop
      nop
      nop
      lw    $3, 0($2)
      mtc0  $3, $1
      nop; nop; nop; nop;
      nop; nop; nop; nop;
  """
    + test_end +
  """
   .data
   .align 4
      tdata_0: .word 0xffff0000
  """ )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 0xffff0000

  return [ mem_delay, sparse_mem_img, expected_result ]

# Test instructions with data hazard due to producer in W stage

def lw_hazard_W():

  asm_str = \
    ( test_start +
  """
      la    $2, tdata_0
      nop
      nop
      lw    $3, 0($2)
      mtc0  $3, $1
      nop; nop; nop; nop;
      nop; nop; nop; nop;
  """
    + test_end +
  """
   .data
   .align 4
      tdata_0: .word 0xffff0000
  """ )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 0xffff0000

  return [ mem_delay, sparse_mem_img, expected_result ]

# Test instructions with data hazard due to producer in M stage

def lw_hazard_M():

  asm_str = \
    ( test_start +
  """
      la    $2, tdata_0
      nop
      lw    $3, 0($2)
      mtc0  $3, $1
      nop; nop; nop; nop;
      nop; nop; nop; nop;
  """
    + test_end +
  """
   .data
   .align 4
      tdata_0: .word 0xffff0000
  """ )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 0xffff0000

  return [ mem_delay, sparse_mem_img, expected_result ]

# Test instructions with data hazard due to producer in X stage

def lw_hazard_X():

  asm_str = \
    ( test_start +
  """
      la    $2, tdata_0
      lw    $3, 0($2)
      mtc0  $3, $1
      nop; nop; nop; nop;
      nop; nop; nop; nop;
  """
    + test_end +
  """
   .data
   .align 4
      tdata_0: .word 0xffff0000
  """ )

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( asm_str = asm_str )
  expected_result = 0xffff0000

  return [ mem_delay, sparse_mem_img, expected_result ]

#---------------------------------------------------------------------------
# VMH File Assembly Tests
#---------------------------------------------------------------------------
# Self-checking VMH file based assembly tests

# VMH Files location

vmh_dir = '../tests/build/vmh/'

# test with no delay

def lw_vmh_delay0():

  test_file = vmh_dir + 'parcv1-lw.vmh'

  mem_delay       = 0
  sparse_mem_img  = SparseMemoryImage( vmh_filename = test_file )
  expected_result = 1

  return [ mem_delay, sparse_mem_img, expected_result ]

# test with delay

def lw_vmh_delay5():

  test_file = vmh_dir + 'parcv1-lw.vmh'

  mem_delay       = 5
  sparse_mem_img  = SparseMemoryImage( vmh_filename = test_file )
  expected_result = 1

  return [ mem_delay, sparse_mem_img, expected_result ]
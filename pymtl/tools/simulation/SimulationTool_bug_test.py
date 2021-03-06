#=======================================================================
# SimulationTool_bug_test.py
#=======================================================================
# Test which reproduces the following issue:
#
#   https://github.com/cornell-brg/pymtl/issues/79
#
# Note that this bug is non-deterministic.

import pytest

from pymtl      import *
from pclib.rtl  import Mux, RightLogicalShifter, LeftLogicalShifter, Adder
from pclib.test import run_test_vector_sim

#-----------------------------------------------------------------------
# test_simple
#-----------------------------------------------------------------------
@pytest.mark.parametrize('i', [(i) for i in range(5)])
def test_simple(i):

  #-----------------------------------------------------------------------
  # Inner
  #-----------------------------------------------------------------------
  #
  # Problematic connection:
  #
  #   top.a -> middle.a[0:2] -> middle.a -> middle.a[0] -> inner.a
  #       0 -> middle.a[2:4] -> ^
  #
  # A slice_cb() function is generated for top.a => middle.a[0:2].
  # This is attached to top.a and is responsible for writing
  # middle.a[0:2].
  #
  # A slice_cb() is also needed for middle.a[0] => inner.a.
  # For **working** runs, this slice_cb seems to be attached to the slice
  # middle.a[0:2]. This is odd since I would expect it to be attached to
  # middle.a and triggered which middle.a[0:2] writes middle.a!
  #
  class Inner( Model ):
    def __init__( s ):
      s.a   = InPort ( 1 )
      s.out = OutPort( 1 )
      @s.combinational
      def logic( ): s.out.value = s.a

  class Middle( Model ):
    def __init__( s ):
      s.a   = InPort ( 4 )
      s.out = OutPort( 1 )
      s.inner = Inner()
      s.connect_dict({
        s.inner.a   : s.a[0],
        s.inner.out : s.out,
      })

  class Top( Model ):
    def __init__( s ):
      s.a   = InPort ( 2 )
      s.out = OutPort( 1 )

      s.middle = Middle()

      s.connect( s.a,   s.middle.a[0:2] )
      s.connect( 0,     s.middle.a[2:4] )
      s.connect( s.out, s.middle.out    )

  #-----------------------------------------------------------------------
  # Inner
  #-----------------------------------------------------------------------
  run_test_vector_sim( Top(), [
    ('a   out*'),
    [  1,   1 ],
    [  2,   0 ],
    [  3,   1 ],
  ])

#-----------------------------------------------------------------------
# IntMulNstageStep
#-----------------------------------------------------------------------
class IntMulNstageStep( Model ):

  # Constructor

  def __init__( s ):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.in_a       = InPort  (32)
    s.in_b       = InPort  (32)
    s.in_result  = InPort  (32)

    s.out_a      = OutPort (32)
    s.out_b      = OutPort (32)
    s.out_result = OutPort (32)

    #---------------------------------------------------------------------
    # Structural composition
    #---------------------------------------------------------------------

    # Right shifter

    s.rshifter = m = RightLogicalShifter(32)
    s.connect_dict({
      m.in_   : s.in_b,
      m.shamt : 1,
      m.out   : s.out_b,
    })

    # Left shifter

    s.lshifter = m = LeftLogicalShifter(32)
    s.connect_dict({
      m.in_   : s.in_a,
      m.shamt : 1,
      m.out   : s.out_a,
    })

    # Adder

    s.add = m = Adder(32)
    s.connect_dict({
      m.in0 : s.in_a,
      m.in1 : s.in_result,
    })

    # Result mux

    s.result_mux = m = Mux(32,2)
    s.connect_dict({
      m.sel    : s.in_b[0],
      m.in_[0] : s.in_result,
      m.in_[1] : s.add.out,
      m.out    : s.out_result
    })

  # Line tracing

  def line_trace( s ):
    return "{}|{}|{}(){}|{}|{}".format(
      s.in_a,  s.in_b,  s.in_result,
      s.out_a, s.out_b, s.out_result
    )

#-----------------------------------------------------------------------
# TestHarness
#-----------------------------------------------------------------------
# Create a 32b x 4b multiplier

class TestHarness( Model ):

  def __init__( s, fix ):

    s.a      = InPort(32)
    s.b      = InPort(4)
    s.result = OutPort(32)

    # Instantiate steps

    s.steps = IntMulNstageStep[4]()

    #---------------------------------------------------------------------
    # DEBUG
    #---------------------------------------------------------------------

    # Performing zero extension by assigning zero to the top bits of in_b
    # fails non-deterministically

    if not fix:

      s.connect( s.b, s.steps[0].in_b[0:4]  )
      s.connect( 0,   s.steps[0].in_b[5:32] )

    # Using an explicit combinational block to do the zero extension seems
    # to work reliably

    else:

      s.temp = Wire(32)

      @s.combinational
      def block():
        s.temp.value = zext( s.b, 32 )

      s.connect( s.temp, s.steps[0].in_b  )

    #---------------------------------------------------------------------
    # /DEBUG
    #---------------------------------------------------------------------

    s.connect( s.a, s.steps[0].in_a       )
    s.connect( 0,   s.steps[0].in_result  )

    # Structural composition for intermediate steps

    for i in xrange(3):
      s.connect( s.steps[i].out_a,      s.steps[i+1].in_a      )
      s.connect( s.steps[i].out_b,      s.steps[i+1].in_b      )
      s.connect( s.steps[i].out_result, s.steps[i+1].in_result )

    # Structural composition for last step

    s.connect( s.result, s.steps[3].out_result  )

  def line_trace( s ):
    return "{}:{}({} {} {} {})".format(
      s.a, s.b,
      s.steps[0].out_result,
      s.steps[1].out_result,
      s.steps[2].out_result,
      s.steps[3].out_result,
    )

#-----------------------------------------------------------------------
# test_32b_x_4b_mult
#-----------------------------------------------------------------------
@pytest.mark.parametrize('i,fix', [(i,i<5) for i in range(10)])
def test_32b_x_4b_mult(i,fix):
  run_test_vector_sim( TestHarness(fix), [
    ('a   b   result*'),
    [  0,  0,   0 ],
    [  2,  3,   6 ],
    [  4,  5,  20 ],
    [  3,  4,  12 ],
    [ 10, 13, 130 ],
    [  8,  7,  56 ],
  ])

import sys, unittest

# attempt to use the most current library
sys.path.insert(0, '..')
from statlib import stats, pstat

try:
    from numpy import array as num_array
except ImportError:
    # numpy not installed
    sys.stderr.write('Numpy not installed ... skipping numpy tests\n')
    # falls back to lists
    def num_array( values ):
        return values

class TestStatlib(unittest.TestCase):
    
    def setUp(self):
        "Gets called on each test"
        # generate list data
        self.L  = self.LF = range( 1, 21 )
        self.LF[2] = 3.0
        self.LL = [ self.L ] * 5

        # array data if numpy is installed
        self.A  = self.AF = num_array( self.L )
        self.AA = num_array( self.LL )
        
        self.EQ = self.assertAlmostEqual

    def test_geometricmean(self):
        "Testing geometric mean"
        data = [ self.L, self.LF, self.A, self.AF  ]
        for d in data :
            self.EQ( stats.geometricmean( d ), 8.304, 3)

    def test_harmonicmean(self):
        "Testing harmonic mean"
        data = [ self.L, self.LF, self.A, self.AF  ]
        for d in data :
            self.EQ( stats.harmonicmean( d ), 5.559, 3)

    def test_mean(self):
        "Testing mean"
        data = [ self.L, self.LF, self.A, self.AF  ]
        for d in data :
            self.EQ( stats.mean( d ), 10.5, 3)

    def test_median(self):
        "Testing median"
        data = [ self.L, self.LF, self.A, self.AF  ]
        for d in data :
            self.assertTrue( 10 < stats.median( d ) < 11 )
    
    def test_medianscore(self):
        "Testing medianscore"
        
        # data of even lenghts
        data1 = [ self.L, self.LF, self.A, self.AF  ]
        for d in data1 :
            self.EQ( stats.medianscore( d ), 10.5 )

        # data with odd lenghts
        L2 = self.L + [ 20 ]
        A2 = num_array( L2 )
        data2 = [ L2, A2  ]
        for d in data2 :
            self.EQ( stats.medianscore( d ), 11 )

        
    def test_mode(self):
        "Testing mode"
        L1 = [1,1,1,2,3,4,5 ]
        L2 = [1,1,1,2,3,4,5,6 ]

        A1 = num_array( L1 )
        A2 = num_array( L2 )
        data = [ L1, L2, A1, A2  ]
        for d in data :
            self.assertEqual( stats.mode( d ), (3, [1]) )

def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase( TestStatlib )
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
"""
Displays code coverage with coverage or figleaf 
in the manner described in

    * coverage: http://nedbatchelder.com/code/modules/coverage.html
    * figleaf: http://darcs.idyll.org/~t/projects/figleaf/README.html
"""

if __name__ == '__main__':
    import unittest

    MODE = 'coverage' 
    MODE = 'figleaf' 

    if MODE == 'coverage':
    
        # coverage with coverage module, will write to standard output
        import coverage
        coverage.erase()
        coverage.start()
        import test_all
        from statlib import stats, pstat
        suite = test_all.get_suite()
        unittest.TextTestRunner(verbosity=2).run(suite)
        coverage.report( [ stats, pstat ] )

    elif MODE == 'figleaf':
     
        # coverage with figleaf, will write to the html directrory
        import figleaf
        from figleaf import annotate_html

        figleaf.start()
        import test_all
        from statlib import stats, pstat
        suite = test_all.get_suite()
        unittest.TextTestRunner(verbosity=2).run(suite)
        figleaf.stop()
        figleaf.write_coverage('.figleaf')
        data = figleaf.get_data().gather_files()
        annotate_html.report_as_html( data, 'html', [] )
    
    else:
        print 'Invalid mode %s' % mode
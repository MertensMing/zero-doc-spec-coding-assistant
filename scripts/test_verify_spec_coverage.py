import unittest
from verify_spec_coverage import check_sequence, analyze_coverage

class TestVerifySpecCoverage(unittest.TestCase):

    def test_valid_sequence(self):
        mss_tests = ["@MSS-1: 第一步", "@MSS-2: 第二步"]
        ext_tests = ["@Ext-1a: 错误一", "@Ext-1b: 错误二", "@Ext-2a: 错误三"]
        errors = check_sequence(mss_tests, ext_tests)
        self.assertEqual(len(errors), 0, f"期望没有错误，但得到: {errors}")

    def test_mss_sequence_gap(self):
        mss_tests = ["@MSS-1: 第一步", "@MSS-3: 第三步"]
        ext_tests = []
        errors = check_sequence(mss_tests, ext_tests)
        self.assertEqual(len(errors), 1)
        self.assertIn("MSS 序号断层", errors[0])

    def test_orphaned_extension(self):
        mss_tests = ["@MSS-1: 第一步"]
        ext_tests = ["@Ext-2a: 孤儿节点"]
        errors = check_sequence(mss_tests, ext_tests)
        self.assertEqual(len(errors), 1)
        self.assertIn("孤儿扩展流程", errors[0])

    def test_ext_sequence_gap(self):
        mss_tests = ["@MSS-1: 第一步"]
        ext_tests = ["@Ext-1a: 错误一", "@Ext-1c: 错误三"]
        errors = check_sequence(mss_tests, ext_tests)
        self.assertEqual(len(errors), 1)
        self.assertIn("Ext 序号断层", errors[0])

    def test_invalid_format(self):
        mss_tests = ["@MSS-one: 格式无效"]
        ext_tests = ["@Ext-1: 格式无效"]
        errors = check_sequence(mss_tests, ext_tests)
        self.assertEqual(len(errors), 2)
        self.assertIn("格式无效", errors[0])
        self.assertIn("格式无效", errors[1])

    def test_analyze_coverage(self):
        test_descriptions = [
            "@MSS-1: 第一步",
            "@Ext-1a: 错误一",
            "某个未打标签的测试"
        ]
        mss, ext, other, seq_errors = analyze_coverage("TestUseCase", test_descriptions)
        
        self.assertEqual(len(mss), 1)
        self.assertEqual(len(ext), 1)
        self.assertEqual(len(other), 1)
        self.assertEqual(len(seq_errors), 0)

if __name__ == '__main__':
    unittest.main()

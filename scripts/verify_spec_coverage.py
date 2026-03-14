import re
import sys
import os
from collections import defaultdict

def parse_tests_from_file(file_path):
    """从文件中解析测试描述及其包含的标签。"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"读取文件出错 {file_path}: {e}")
        return None, []

    # 1. 查找是否有 @UseCase
    usecase_pattern = re.compile(r"describe\s*\(\s*['\"](.*?)@UseCase(.*?)\s*['\"]")
    usecase_match = usecase_pattern.search(content)
    usecase_name = usecase_match.group(2).strip() if usecase_match else None

    # 2. 查找所有的 it('...') 或 test('...')
    test_pattern = re.compile(r"(?:it|test)\s*\(\s*['\"](.*?)['\"]")
    matches = test_pattern.findall(content)
    
    return usecase_name, matches

def check_sequence(mss_tests, ext_tests):
    """检查 MSS 和 Ext 标签的序列递增和映射关系。"""
    errors = []
    
    # 提取 MSS 序号 (如 @MSS-1 -> 1)
    mss_ids = []
    mss_pattern = re.compile(r"@MSS-(\d+)")
    for desc in mss_tests:
        match = mss_pattern.search(desc)
        if match:
            mss_ids.append(int(match.group(1)))
        else:
            errors.append(f"❌ 格式无效: '{desc}'。期望的格式为: @MSS-[数字]")
            
    # 检查 MSS 序号是否连续递增
    if mss_ids:
        expected_id = 1
        for mss_id in sorted(mss_ids):
            if mss_id != expected_id:
                errors.append(f"❌ MSS 序号断层: 期望 @MSS-{expected_id}，实际找到 @MSS-{mss_id}")
                expected_id = mss_id + 1
            else:
                expected_id += 1
                
    # 提取并检查 Ext 映射和字母顺序 (如 @Ext-2a -> step 2, sub a)
    ext_pattern = re.compile(r"@Ext-(\d+)([a-z]+)")
    ext_groups = defaultdict(list)
    
    for desc in ext_tests:
        match = ext_pattern.search(desc)
        if match:
            step_id = int(match.group(1))
            sub_id = match.group(2)
            ext_groups[step_id].append((sub_id, desc))
            
            # 检查 Ext 是否有对应的 MSS 步骤
            if step_id not in mss_ids:
                errors.append(f"❌ 孤儿扩展流程: '{desc}'。步骤 {step_id} 在 @MSS 中不存在。")
        else:
            errors.append(f"❌ 格式无效: '{desc}'。期望的格式为: @Ext-[数字][字母] (例如 @Ext-2a)")

    # 检查每个步骤的字母是否按 a, b, c 递增
    for step_id, subs in ext_groups.items():
        # subs 是一个元组列表: [(a, desc1), (c, desc2)]
        subs.sort(key=lambda x: x[0])
        expected_char = ord('a')
        
        for sub_id, desc in subs:
            if len(sub_id) == 1: # 目前只处理单个字母的递增检查
                current_char = ord(sub_id)
                if current_char != expected_char:
                    errors.append(f"❌ 步骤 {step_id} 的 Ext 序号断层: 期望字母 '{chr(expected_char)}'，在 '{desc}' 中找到的是 '{sub_id}'")
                    expected_char = current_char + 1
                else:
                    expected_char += 1

    return errors

def analyze_coverage(usecase_name, test_descriptions):
    """分析测试用例是否遵循 Zero-Doc Spec 结构规范。"""
    mss_tests = []
    ext_tests = []
    other_tests = []
    
    for desc in test_descriptions:
        if '@MSS' in desc:
            mss_tests.append(desc)
        elif '@Ext' in desc:
            ext_tests.append(desc)
        else:
            other_tests.append(desc)
            
    seq_errors = check_sequence(mss_tests, ext_tests)
            
    return mss_tests, ext_tests, other_tests, seq_errors

def main():
    if len(sys.argv) < 2:
        print("用法: python verify_spec_coverage.py <文件路径>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"错误: 找不到文件 {file_path}。")
        sys.exit(1)
        
    usecase_name, test_descriptions = parse_tests_from_file(file_path)
    
    if usecase_name is None:
        print(f"⚠️ 在 {file_path} 的 describe 块中未找到 @UseCase 标签")
        print("💡 建议: 请确保最外层的 describe 块格式如下: describe('@UseCase [你的用例名称]: ...')")
        sys.exit(0)
        
    mss_tests, ext_tests, other_tests, seq_errors = analyze_coverage(usecase_name, test_descriptions)
    
    # 生成报告
    print(f"# Zero-Doc 契约审查报告: {os.path.basename(file_path)}")
    print(f"- 业务用例 (UseCase): {usecase_name}")
    print(f"\n## 覆盖率统计")
    print(f"- @MSS (主成功场景) 测试数: {len(mss_tests)}")
    print(f"- @Ext (扩展分支) 测试数: {len(ext_tests)}")
    print(f"- 未打标签的测试数: {len(other_tests)}")
    
    has_errors = False
    
    if len(mss_tests) == 0:
        print("\n❌ 错误: 缺少 @MSS 测试。一个用例 (UseCase) 必须至少包含一个主成功场景 (Main Success Scenario)。")
        has_errors = True
        
    if seq_errors:
        print("\n## 🚨 序列与映射错误 (防腐化检查)")
        for err in seq_errors:
            print(err)
        has_errors = True
        
    if len(other_tests) > 0:
        print("\n⚠️ 警告: 发现未打标签的测试。在 Zero-Doc 规范中，所有的测试都应该归属于 @MSS 或 @Ext。")
        for test in other_tests:
            print(f"  - {test}")
            
    if not has_errors and len(other_tests) == 0:
         print("\n✅ Zero-Doc 结构审查通过！所有的序列递增和映射关系均正确。")

if __name__ == "__main__":
    main()

"""
系统管理菜单处理器
负责系统配置和管理相关功能的用户界面和交互处理
遵循重构后的分层架构原则
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from scripts.cli.base_menu_handler import BaseMenuHandler
from scripts.core.content_pipeline import ContentPipeline


class SystemMenuHandler(BaseMenuHandler):
    """系统管理菜单处理器"""
    
    def __init__(self, pipeline: ContentPipeline):
        """
        初始化系统菜单处理器
        
        Args:
            pipeline: 内容管道实例
        """
        super().__init__(pipeline, "系统管理")
    
    def handle_llm_engine_menu(self) -> Optional[str]:
        """
        处理LLM引擎切换菜单
        
        Returns:
            处理结果或None
        """
        menu_title = "🤖 LLM引擎切换管理"
        menu_description = "💡 管理AI引擎使用模式和配置"
        
        # 检查当前状态
        status_info = self._get_current_engine_status()
        
        print(f"\n📊 当前状态:")
        print(f"   • 当前引擎: {status_info['engine']}")
        print(f"   • 引擎状态: {status_info['status']}")
        print(f"   • 模型信息: {status_info['model_info']}")
        
        print("\n💡 使用模式说明：")
        print("   • Claude: 使用您的Claude Pro订阅 ($20/月)")
        print("   • 千问3-code: 备用API引擎 (阿里云)")
        print("   • Kimi K2: 备用API引擎 (月之暗面, 高性价比)")
        print("\n⚠️  注意事项：")
        print("   • 当Claude Pro达到月度限制时，可切换到备用引擎")
        print("   • 备用引擎按使用量付费，适合突发需求")
        
        options = [
            "1. 🏠 恢复Claude Pro模式 (默认)",
            "2. 🔄 切换到千问3-code引擎",
            "3. 🌙 切换到Kimi K2引擎",
            "4. 📋 查看引擎配置详情",
            "5. 🧪 测试当前引擎连接",
            "6. 🔧 重置引擎配置",
            "7. 📝 生成WSL环境变量设置脚本"
        ]
        
        handlers = [
            self._restore_claude_pro_mode,
            self._switch_to_qwen_engine,
            self._switch_to_kimi_engine,
            self._show_engine_config_details,
            self._test_current_engine_connection,
            self._reset_engine_config,
            self._generate_wsl_env_script
        ]
        
        return self.create_menu_loop_with_path(menu_title, menu_description, options, handlers, "9.2")
    
    def _get_current_engine_status(self) -> Dict[str, str]:
        """获取当前引擎状态信息"""
        current_base_url = os.getenv('ANTHROPIC_BASE_URL', '')
        current_api_key = os.getenv('ANTHROPIC_API_KEY', '')
        
        if current_base_url and 'dashscope.aliyuncs.com' in current_base_url:
            return {
                'engine': "千问3-code (Qwen)",
                'status': "🟢 活跃",
                'model_info': "qwen3-code (1万亿参数MoE)"
            }
        elif current_base_url and 'moonshot.ai' in current_base_url:
            return {
                'engine': "Kimi K2 (Moonshot)",
                'status': "🟢 活跃", 
                'model_info': "kimi-k2 (1万亿参数MoE, 128K上下文)"
            }
        elif current_api_key:
            return {
                'engine': "Claude Pro (官方)",
                'status': "🟢 活跃",
                'model_info': "claude-3.5-sonnet (官方API)"
            }
        else:
            return {
                'engine': "Claude Pro (默认)",
                'status': "🟡 默认模式",
                'model_info': "claude-3.5-sonnet (无API配置)"
            }
    
    def _restore_claude_pro_mode(self) -> Optional[str]:
        """恢复Claude Pro模式"""
        self.display_menu_header("🏠 恢复Claude Pro模式",
                                "清除API配置，恢复默认Claude Pro模式")
        
        try:
            # 清除所有API配置，恢复默认Claude Pro模式
            env_vars_to_clear = ['ANTHROPIC_BASE_URL', 'ANTHROPIC_AUTH_TOKEN', 'ANTHROPIC_API_KEY']
            cleared_vars = []
            
            # 清除运行时环境变量
            for var in env_vars_to_clear:
                if var in os.environ:
                    del os.environ[var]
                    cleared_vars.append(var)
            
            # 持久化到.env文件
            clear_config = {var: "" for var in env_vars_to_clear}
            self._update_env_file(clear_config, clear=True)
            
            print("✅ Claude Pro模式已恢复")
            if cleared_vars:
                print(f"🗑️  已清除环境变量: {', '.join(cleared_vars)}")
            else:
                print("💡 已经在Claude Pro模式下")
            
            self.log_action("恢复Claude Pro模式", f"清除变量: {cleared_vars}")
            
            # 重新启动提示
            print("\n⚠️  重要提示:")
            print("   • 需要重启终端或运行 'source .env' 使配置生效")
            print("   • WSL用户建议运行生成的环境变量脚本")
            
            return "Claude Pro模式已恢复"
            
        except Exception as e:
            self.handle_error(e, "恢复Claude Pro模式")
            return None
    
    def _switch_to_qwen_engine(self) -> Optional[str]:
        """切换到千问3-code引擎"""
        self.display_menu_header("🔄 切换到千问3-code引擎",
                                "配置阿里云千问API作为备用引擎")
        
        print("📋 千问3-code引擎配置:")
        print("   • 供应商: 阿里云")
        print("   • 模型: qwen3-code (1万亿参数MoE)")
        print("   • 特点: 代码生成能力强，中文友好")
        print("   • 费用: 按使用量付费")
        
        # 检查是否已有配置
        existing_key = os.getenv('QWEN_API_KEY', '')
        if not existing_key:
            print("\n⚠️  需要先配置QWEN_API_KEY")
            api_key = input("请输入阿里云千问API密钥 (留空取消): ").strip()
            if not api_key:
                self.display_operation_cancelled()
                return None
        else:
            print(f"\n✅ 检测到已配置的API密钥: {existing_key[:8]}...")
            if not self.confirm_operation("是否使用现有配置？"):
                api_key = input("请输入新的阿里云千问API密钥: ").strip()
                if not api_key:
                    self.display_operation_cancelled()
                    return None
            else:
                api_key = existing_key
        
        try:
            # 配置千问引擎环境变量
            env_config = {
                'ANTHROPIC_BASE_URL': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                'ANTHROPIC_API_KEY': api_key,
                'QWEN_API_KEY': api_key  # 备份保存
            }
            
            # 更新运行时环境变量
            for key, value in env_config.items():
                os.environ[key] = value
            
            # 持久化到.env文件
            self._update_env_file(env_config)
            
            self.display_success_message("千问3-code引擎配置完成")
            self.log_action("切换到千问3-code引擎", "配置完成")
            
            print("🎯 配置详情:")
            print(f"   • Base URL: {env_config['ANTHROPIC_BASE_URL']}")
            print(f"   • API Key: {api_key[:8]}...{api_key[-4:]}")
            
            return "千问3-code引擎已配置"
            
        except Exception as e:
            self.handle_error(e, "切换到千问3-code引擎")
            return None
    
    def _switch_to_kimi_engine(self) -> Optional[str]:
        """切换到Kimi K2引擎"""
        self.display_menu_header("🌙 切换到Kimi K2引擎",
                                "配置月之暗面Kimi API作为备用引擎")
        
        print("📋 Kimi K2引擎配置:")
        print("   • 供应商: 月之暗面 (Moonshot)")
        print("   • 模型: kimi-k2 (1万亿参数MoE)")
        print("   • 特点: 128K上下文，高性价比")
        print("   • 费用: 按使用量付费")
        
        # 检查是否已有配置
        existing_key = os.getenv('MOONSHOT_API_KEY', '')
        if not existing_key:
            print("\n⚠️  需要先配置MOONSHOT_API_KEY")
            api_key = input("请输入月之暗面API密钥 (留空取消): ").strip()
            if not api_key:
                self.display_operation_cancelled()
                return None
        else:
            print(f"\n✅ 检测到已配置的API密钥: {existing_key[:8]}...")
            if not self.confirm_operation("是否使用现有配置？"):
                api_key = input("请输入新的月之暗面API密钥: ").strip()
                if not api_key:
                    self.display_operation_cancelled()
                    return None
            else:
                api_key = existing_key
        
        try:
            # 配置Kimi引擎环境变量
            env_config = {
                'ANTHROPIC_BASE_URL': 'https://api.moonshot.cn/v1',
                'ANTHROPIC_API_KEY': api_key,
                'MOONSHOT_API_KEY': api_key  # 备份保存
            }
            
            # 更新运行时环境变量
            for key, value in env_config.items():
                os.environ[key] = value
            
            # 持久化到.env文件
            self._update_env_file(env_config)
            
            self.display_success_message("Kimi K2引擎配置完成")
            self.log_action("切换到Kimi K2引擎", "配置完成")
            
            print("🎯 配置详情:")
            print(f"   • Base URL: {env_config['ANTHROPIC_BASE_URL']}")
            print(f"   • API Key: {api_key[:8]}...{api_key[-4:]}")
            
            return "Kimi K2引擎已配置"
            
        except Exception as e:
            self.handle_error(e, "切换到Kimi K2引擎")
            return None
    
    def _show_engine_config_details(self) -> Optional[str]:
        """显示引擎配置详情"""
        self.display_menu_header("📋 引擎配置详情",
                                "查看当前所有引擎相关配置")
        
        print("🔍 环境变量配置:")
        env_vars = [
            ('ANTHROPIC_BASE_URL', 'Anthropic API Base URL'),
            ('ANTHROPIC_API_KEY', 'Anthropic API Key'),
            ('ANTHROPIC_AUTH_TOKEN', 'Anthropic Auth Token'),
            ('QWEN_API_KEY', '阿里云千问API密钥'),
            ('MOONSHOT_API_KEY', '月之暗面API密钥')
        ]
        
        for var_name, description in env_vars:
            value = os.getenv(var_name, '')
            if value:
                masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else value
                print(f"   ✅ {description}: {masked_value}")
            else:
                print(f"   ❌ {description}: 未配置")
        
        print("\n📂 配置文件检查:")
        config_files = ['.env', '.env.local', '.env.example']
        for config_file in config_files:
            file_path = Path(config_file)
            if file_path.exists():
                file_size = file_path.stat().st_size
                print(f"   ✅ {config_file}: {file_size} bytes")
            else:
                print(f"   ❌ {config_file}: 不存在")
        
        # 显示当前引擎状态
        status_info = self._get_current_engine_status()
        print(f"\n📊 当前引擎状态:")
        print(f"   • 引擎: {status_info['engine']}")
        print(f"   • 状态: {status_info['status']}")
        print(f"   • 模型: {status_info['model_info']}")
        
        self.pause_for_user()
        return None
    
    def _test_current_engine_connection(self) -> Optional[str]:
        """测试当前引擎连接"""
        self.display_menu_header("🧪 测试当前引擎连接",
                                "验证当前配置的引擎是否可用")
        
        try:
            import subprocess
            import sys
            
            print("🔍 正在测试Gemini模型连接...")
            
            # 调用Gemini验证工具
            result = subprocess.run([
                sys.executable, "scripts/tools/verify_gemini_model.py"
            ], capture_output=True, text=True, timeout=30)
            
            print(result.stdout)
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            
            if result.returncode == 0:
                print("✅ AI引擎连接测试通过")
                return "AI引擎连接正常"
            else:
                print("❌ AI引擎连接测试失败")
                return None
                
        except subprocess.TimeoutExpired:
            print("⏰ 连接测试超时")
            return None
        except Exception as e:
            print(f"❌ 测试过程出错: {e}")
            return None
        
        self.pause_for_user()
        return None
    
    def _reset_engine_config(self) -> Optional[str]:
        """重置引擎配置"""
        self.display_menu_header("🔧 重置引擎配置",
                                "清除所有引擎配置，恢复初始状态")
        
        if not self.confirm_operation("⚠️  这将清除所有LLM引擎配置，确认继续？"):
            self.display_operation_cancelled()
            return None
        
        try:
            # 清除所有相关环境变量
            env_vars_to_clear = [
                'ANTHROPIC_BASE_URL', 'ANTHROPIC_AUTH_TOKEN', 'ANTHROPIC_API_KEY',
                'QWEN_API_KEY', 'MOONSHOT_API_KEY'
            ]
            
            cleared_vars = []
            for var in env_vars_to_clear:
                if var in os.environ:
                    del os.environ[var]
                    cleared_vars.append(var)
            
            # 持久化到.env文件
            clear_config = {var: "" for var in env_vars_to_clear}
            self._update_env_file(clear_config, clear=True)
            
            self.display_success_message("引擎配置已重置")
            print(f"🗑️  已清除 {len(cleared_vars)} 个环境变量")
            self.log_action("重置引擎配置", f"清除变量: {cleared_vars}")
            
            return "引擎配置已重置"
            
        except Exception as e:
            self.handle_error(e, "重置引擎配置")
            return None
    
    def _generate_wsl_env_script(self) -> Optional[str]:
        """生成WSL环境变量设置脚本"""
        self.display_menu_header("📝 生成WSL环境变量设置脚本",
                                "创建用于WSL的环境变量导出脚本")
        
        try:
            script_content = self._create_wsl_export_script()
            
            script_path = Path("set_claude_env.sh")
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # 设置执行权限
            import stat
            script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
            
            self.display_success_message(f"WSL环境脚本已生成: {script_path}")
            print("📝 使用方法:")
            print(f"   1. source {script_path}")
            print(f"   2. 或者: chmod +x {script_path} && ./{script_path}")
            
            self.log_action("生成WSL环境变量脚本", str(script_path))
            return str(script_path)
            
        except Exception as e:
            self.handle_error(e, "生成WSL环境变量脚本")
            return None
    
    def _update_env_file(self, env_config: Dict[str, str], clear: bool = False):
        """更新.env文件"""
        env_file = Path(".env")
        
        if clear and env_config:
            # 清除指定的环境变量
            if env_file.exists():
                lines = env_file.read_text(encoding='utf-8').splitlines()
                new_lines = []
                for line in lines:
                    if '=' in line:
                        key = line.split('=')[0]
                        if key not in env_config:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
                
                env_file.write_text('\\n'.join(new_lines) + '\\n', encoding='utf-8')
        elif env_config:
            # 更新环境变量
            existing_lines = []
            if env_file.exists():
                existing_lines = env_file.read_text(encoding='utf-8').splitlines()
            
            # 创建新的行列表
            new_lines = []
            updated_keys = set()
            
            # 更新现有行
            for line in existing_lines:
                if '=' in line:
                    key = line.split('=')[0]
                    if key in env_config:
                        new_lines.append(f"{key}={env_config[key]}")
                        updated_keys.add(key)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            # 添加新的配置项
            for key, value in env_config.items():
                if key not in updated_keys:
                    new_lines.append(f"{key}={value}")
            
            env_file.write_text('\\n'.join(new_lines) + '\\n', encoding='utf-8')
    
    def _create_wsl_export_script(self) -> str:
        """创建WSL导出脚本内容"""
        current_time = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        script_content = f"""#!/bin/bash
# WSL环境变量设置脚本
# 生成时间: {current_time}
# 用法: source set_claude_env.sh

echo "🔧 设置Claude LLM引擎环境变量..."

# 检查当前配置
"""
        
        # 添加当前环境变量配置
        env_vars = ['ANTHROPIC_BASE_URL', 'ANTHROPIC_API_KEY', 'QWEN_API_KEY', 'MOONSHOT_API_KEY']
        for var in env_vars:
            value = os.getenv(var, '')
            if value:
                script_content += f'export {var}="{value}"\\n'
                script_content += f'echo "✅ 已设置 {var}"\\n'
        
        script_content += """
echo "🎯 环境变量设置完成"
echo "💡 可运行 'env | grep ANTHROPIC' 查看配置"
"""
        
        return script_content
    
    def handle_audio_tools_menu(self) -> None:
        """语音和音频工具菜单 (合并原功能12+相关)"""
        menu_title = "🔊 语音和音频工具"
        menu_description = "🎙️ TTS服务管理和音频处理工具"
        
        options = [
            "1. TTS语音测试",
            "2. 音频质量评估", 
            "3. 语音服务切换",
            "4. 音频格式转换"
        ]
        
        handlers = [
            self._tts_voice_test,
            self._audio_quality_assessment,
            self._voice_service_switch,
            self._audio_format_conversion
        ]
        
        self.create_menu_loop_with_path(menu_title, menu_description, options, handlers, "7")
    
    def _tts_voice_test(self) -> Optional[str]:
        """TTS语音测试 (原ElevenLabs测试)"""
        self.display_menu_header("🎙️ ElevenLabs语音测试工具", "测试TTS服务和语音合成功能")
        
        test_options = [
            "1. API权限检查",
            "2. 声音测试器（完整功能）", 
            "3. 双人对话功能测试",
            "4. 查看配置状态",
            "5. 查看测试结果",
            "6. 快速开始指南",
            "7. 功能使用说明"
        ]
        
        test_handlers = [
            self._elevenlabs_permission_check,
            self._elevenlabs_voice_tester,
            self._elevenlabs_dialogue_test,
            self._elevenlabs_config_status,
            self._elevenlabs_test_results,
            self._elevenlabs_quick_guide,
            self._elevenlabs_usage_guide
        ]
        
        return self.create_menu_loop_with_path("🎙️ ElevenLabs测试", "", test_options, test_handlers, "7.1")
    
    def _elevenlabs_permission_check(self) -> Optional[str]:
        """ElevenLabs API权限检查"""
        try:
            import subprocess
            print("\n🔍 执行ElevenLabs API权限检查...")
            self.log_action("执行ElevenLabs API权限检查")
            
            result = subprocess.run([
                "python", "scripts/tools/elevenlabs/elevenlabs_permission_check.py"
            ], capture_output=False, text=True, check=False)
            
            if result.returncode != 0:
                print("⚠️ 权限检查执行异常，请检查ElevenLabs配置")
                return None
            else:
                return "权限检查完成"
                
        except Exception as e:
            self.handle_error(e, "ElevenLabs权限检查")
            return None
    
    def _elevenlabs_voice_tester(self) -> Optional[str]:
        """ElevenLabs声音测试器"""
        try:
            import subprocess
            print("\n🎙️ 启动ElevenLabs声音测试器...")
            print("💡 提示: 推荐选择以下测试选项:")
            print("   • 选项2: 获取可用TTS模型")
            print("   • 选项4: 创建双人对话播客测试") 
            print("   • 选项7: 完整测试流程")
            print()
            
            self.log_action("启动ElevenLabs声音测试器")
            subprocess.run(["python", "scripts/tools/elevenlabs/elevenlabs_voice_tester.py"])
            return "声音测试器执行完成"
            
        except Exception as e:
            self.handle_error(e, "ElevenLabs声音测试器")
            return None
    
    def _elevenlabs_dialogue_test(self) -> Optional[str]:
        """ElevenLabs双人对话功能测试"""
        try:
            import subprocess
            print("\n🎬 执行ElevenLabs双人对话功能测试...")
            self.log_action("执行ElevenLabs双人对话功能测试")
            
            result = subprocess.run([
                "python", "scripts/tools/elevenlabs/elevenlabs_voice_test.py", "dialogue"
            ], capture_output=False, text=True, check=False)
            
            if result.returncode == 0:
                print("✅ 双人对话功能测试成功")
                return "双人对话测试成功"
            else:
                print("⚠️ 双人对话功能测试异常")
                return None
                
        except Exception as e:
            self.handle_error(e, "ElevenLabs双人对话测试")
            return None
    
    def _elevenlabs_config_status(self) -> Optional[str]:
        """查看ElevenLabs配置状态"""
        try:
            import os
            from pathlib import Path
            
            print("\n📊 ElevenLabs配置状态")
            print("="*40)
            
            # 检查API密钥
            elevenlabs_key = os.getenv('ELEVENLABS_API_KEY', '')
            print(f"🔑 API密钥: {'✅ 已配置 (' + elevenlabs_key[:10] + '...)' if elevenlabs_key else '❌ 未配置'}")
            
            # 检查配置文件
            config_file = Path("config/elevenlabs_voices.yml")
            template_file = Path("config/elevenlabs_voices_template.yml")
            print(f"📋 配置文件: {'✅ 存在' if config_file.exists() else '❌ 缺失'}")
            print(f"📋 模板文件: {'✅ 存在' if template_file.exists() else '❌ 缺失'}")
            
            # 检查测试目录
            test_dir = Path("tests/elevenlabs_voice_tests")
            print(f"📁 测试目录: {'✅ 存在' if test_dir.exists() else '❌ 缺失'}")
            
            # 检查依赖库
            try:
                import elevenlabs
                print("✅ elevenlabs: 已安装")
            except ImportError:
                print("❌ elevenlabs: 未安装")
                print("💡 请运行: pip install elevenlabs")
            
            self.pause_for_user()
            return "配置状态检查完成"
            
        except Exception as e:
            self.handle_error(e, "ElevenLabs配置状态检查")
            return None
    
    def _elevenlabs_test_results(self) -> Optional[str]:
        """查看ElevenLabs测试结果"""
        try:
            from pathlib import Path
            
            print("\n📊 ElevenLabs测试结果")
            print("="*40)
            
            test_dir = Path("tests/elevenlabs_voice_tests")
            if test_dir.exists():
                audio_files = list(test_dir.glob("*.mp3")) + list(test_dir.glob("*.wav"))
                if audio_files:
                    print(f"🎵 发现 {len(audio_files)} 个测试音频文件:")
                    for i, file in enumerate(audio_files[-10:], 1):  # 显示最新10个
                        print(f"   {i}. {file.name}")
                else:
                    print("📂 测试目录存在，但暂无音频文件")
            else:
                print("📂 测试目录不存在")
                print("💡 请先运行声音测试器生成测试文件")
            
            self.pause_for_user()
            return "测试结果查看完成"
            
        except Exception as e:
            self.handle_error(e, "ElevenLabs测试结果查看")
            return None
    
    def _elevenlabs_quick_guide(self) -> Optional[str]:
        """ElevenLabs快速开始指南"""
        guide_text = """
🚀 ElevenLabs快速开始指南
================================================

📋 准备步骤:
1. 注册ElevenLabs账户 (https://elevenlabs.io)
2. 获取API密钥并添加到.env文件:
   ELEVENLABS_API_KEY=your_api_key_here
3. 安装依赖: pip install elevenlabs

🔧 基础测试流程:
1. 先运行"API权限检查"确认配置正确
2. 使用"声音测试器"进行完整功能测试
3. 尝试"双人对话功能测试"体验高级功能

💡 使用建议:
• 免费账户每月有10,000字符限制
• 推荐使用Pro账户获得更多语音选择
• 测试文件会保存到tests/elevenlabs_voice_tests/目录

📖 更多信息:
• 查看docs/elevenlabs_pro_guide.md了解Pro功能
• 使用config/elevenlabs_voices.yml自定义语音配置
        """
        
        print(guide_text)
        self.pause_for_user()
        return "快速指南查看完成"
    
    def _elevenlabs_usage_guide(self) -> Optional[str]:
        """ElevenLabs功能使用说明"""
        usage_text = """
📖 ElevenLabs功能使用说明
================================================

🛠️ 各功能详解:

1. API权限检查
   • 验证API密钥有效性
   • 检查配额使用情况
   • 确认Pro功能可用性

2. 声音测试器
   • 测试所有可用语音
   • 生成示例音频文件
   • 支持自定义文本转换

3. 双人对话功能测试
   • 模拟两人对话场景
   • 使用不同语音角色
   • 适用于播客制作

4. 配置管理
   • 查看当前配置状态
   • 检查必需文件和依赖
   • 提供配置修复建议

🔧 配置文件说明:
• elevenlabs_voices.yml - 基础语音配置
• elevenlabs_voices_pro.yml - Pro功能配置
• elevenlabs_voices_template.yml - 配置模板

⚠️ 常见问题:
• API密钥无效 -> 检查密钥格式和权限
• 配额不足 -> 升级账户或等待重置
• 语音质量差 -> 尝试不同的语音模型
        """
        
        print(usage_text)
        self.pause_for_user()
        return "使用说明查看完成"
    
    def _audio_quality_assessment(self) -> Optional[str]:
        """音频质量评估"""
        print("\n📊 音频质量评估")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _voice_service_switch(self) -> Optional[str]:
        """语音服务切换"""
        print("\n🔄 语音服务切换")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _audio_format_conversion(self) -> Optional[str]:
        """音频格式转换"""
        print("\n🔊 音频格式转换")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def handle_system_tools_menu(self) -> None:
        """系统工具集合菜单 (合并原功能7+10+11)"""
        menu_title = "⚙️ 系统工具集合"
        menu_description = "🛠️ 系统维护和配置管理"
        
        options = [
            "1. 系统状态检查",
            "2. LLM引擎切换",
            "3. 调试和维护",
            "4. 配置管理",
            "5. 日志查看"
        ]
        
        handlers = [
            self._system_status_check,
            self._llm_engine_switch,
            self._debug_maintenance,
            self._config_management,
            self._log_viewer
        ]
        
        self.create_menu_loop_with_path(menu_title, menu_description, options, handlers, "9")
    
    def _system_status_check(self) -> Optional[str]:
        """系统状态检查 (原功能7)"""
        print("\n🔍 系统状态检查")
        
        try:
            import subprocess
            import sys
            from pathlib import Path
            
            print("🔍 正在检查系统状态...")
            
            # 检查WeChat发布系统状态
            print("\n📱 微信发布系统状态:")
            result = subprocess.run([
                sys.executable, "scripts/tools/wechat_system_verify.py"
            ], capture_output=True, text=True, timeout=30)
            
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            
            # 检查核心目录状态
            print("\n📁 核心目录状态:")
            important_dirs = [
                Path("_posts"),
                Path("_drafts"), 
                Path("config"),
                Path("scripts"),
                Path("assets"),
                Path("_data")
            ]
            
            for dir_path in important_dirs:
                status = "✅ 存在" if dir_path.exists() else "❌ 缺失"
                print(f"  {dir_path}: {status}")
            
            # 检查关键配置文件
            print("\n⚙️ 关键配置文件:")
            config_files = [
                Path("config/onedrive_config.json"),
                Path("config/youtube_oauth_credentials.json"),
                Path("_config.yml"),
                Path(".env")
            ]
            
            for config_file in config_files:
                status = "✅ 存在" if config_file.exists() else "❌ 缺失"
                print(f"  {config_file.name}: {status}")
            
            # 检查虚拟环境
            print("\n🐍 Python环境:")
            import sys
            print(f"  Python版本: {sys.version}")
            virtual_env = os.environ.get('VIRTUAL_ENV')
            if virtual_env:
                print(f"  虚拟环境: ✅ {virtual_env}")
            else:
                print("  虚拟环境: ❌ 未激活")
            
            print("✅ 系统状态检查完成")
            return "系统状态检查完成"
            
        except subprocess.TimeoutExpired:
            print("⏰ 系统检查超时")
            return None
        except Exception as e:
            print(f"❌ 系统检查出错: {e}")
            return None
        
        self.pause_for_user()
        return None
    
    def _llm_engine_switch(self) -> Optional[str]:
        """LLM引擎切换 (原功能10)"""
        return self.handle_llm_engine_menu()
    
    def _debug_maintenance(self) -> Optional[str]:
        """调试和维护 (原功能11)"""
        print("\n🔧 调试和维护")
        print("🛠️ 系统调试和问题诊断工具")
        
        try:
            while True:
                print("\n🔧 调试和维护选项:")
                print("1. OAuth授权问题诊断")
                print("2. 检查GitHub令牌状态")
                print("3. 路径计算问题修复")
                print("4. 功能回归测试")
                print("5. 导入路径修复")
                print("0. 返回上级菜单")
                
                choice = input("\n请选择操作 (1-5/0): ").strip()
                
                if choice == "1":
                    print("\n🔍 OAuth授权问题诊断...")
                    import subprocess
                    import sys
                    
                    result = subprocess.run([
                        sys.executable, "scripts/tools/oauth/oauth_debug.py"
                    ], check=False)
                    
                    if result.returncode == 0:
                        print("✅ OAuth诊断完成")
                    else:
                        print("❌ OAuth诊断发现问题")
                
                elif choice == "2":
                    print("\n🔑 检查GitHub令牌状态...")
                    result = subprocess.run([
                        sys.executable, "scripts/tools/checks/check_github_token.py"
                    ], check=False)
                    
                    if result.returncode == 0:
                        print("✅ GitHub令牌检查完成")
                    else:
                        print("❌ GitHub令牌检查发现问题")
                
                elif choice == "3":
                    print("\n📐 路径计算问题修复...")
                    result = subprocess.run([
                        sys.executable, "scripts/tools/checks/fix_path_calculations.py"
                    ], check=False)
                    
                    if result.returncode == 0:
                        print("✅ 路径计算修复完成")
                    else:
                        print("❌ 路径计算修复失败")
                
                elif choice == "4":
                    print("\n🧪 功能回归测试...")
                    result = subprocess.run([
                        sys.executable, "scripts/tools/testing/function_regression_test.py"
                    ], check=False)
                    
                    if result.returncode == 0:
                        print("✅ 功能回归测试完成")
                    else:
                        print("❌ 功能回归测试发现问题")
                
                elif choice == "5":
                    print("\n🔧 导入路径修复...")
                    result = subprocess.run([
                        sys.executable, "scripts/tools/checks/fix_import_paths.py"
                    ], check=False)
                    
                    if result.returncode == 0:
                        print("✅ 导入路径修复完成")
                    else:
                        print("❌ 导入路径修复失败")
                
                elif choice == "0":
                    break
                
                else:
                    print("❌ 无效选择")
                
                if choice != "0":
                    input("\n按回车键继续...")
            
            return "调试和维护完成"
            
        except Exception as e:
            print(f"❌ 调试和维护出错: {e}")
            self.pause_for_user()
            return None
    
    def _config_management(self) -> Optional[str]:
        """配置管理"""
        print("\n⚙️ 配置管理")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _log_viewer(self) -> Optional[str]:
        """日志查看"""
        try:
            from pathlib import Path
            import os
            from datetime import datetime
            
            print("\n📋 系统日志查看")
            print("="*40)
            
            # 定义日志目录和文件
            log_locations = [
                Path(".build/logs/pipeline.log"),
                Path("logs/onedrive_blog_images.log"), 
                Path(".build/logs/onedrive_blog_images.log")
            ]
            
            # 查找存在的日志文件
            available_logs = []
            for log_path in log_locations:
                if log_path.exists():
                    stat = log_path.stat()
                    size_mb = stat.st_size / (1024 * 1024)
                    modified = datetime.fromtimestamp(stat.st_mtime)
                    available_logs.append({
                        'path': log_path,
                        'size': size_mb,
                        'modified': modified,
                        'name': log_path.name
                    })
            
            if not available_logs:
                print("📂 未找到系统日志文件")
                print("💡 日志文件可能在系统首次运行后生成")
                self.pause_for_user()
                return None
            
            # 显示可用日志
            print(f"📊 发现 {len(available_logs)} 个日志文件:")
            for i, log in enumerate(available_logs, 1):
                print(f"   {i}. {log['name']}")
                print(f"      大小: {log['size']:.2f}MB")
                print(f"      修改: {log['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
                print()
            
            # 日志查看选项
            while True:
                print("日志查看选项:")
                print("1. 📄 查看最新日志 (最后50行)")
                print("2. 🔍 搜索日志内容")
                print("3. 📊 日志统计信息")
                print("4. 🧹 清理旧日志")
                print("0. 返回")
                
                choice = input("\n请选择 (0-4): ").strip()
                
                if choice == "0":
                    break
                elif choice == "1":
                    self._show_recent_logs(available_logs)
                elif choice == "2":
                    self._search_logs(available_logs)
                elif choice == "3":
                    self._show_log_stats(available_logs)
                elif choice == "4":
                    self._cleanup_logs(available_logs)
                else:
                    print("❌ 无效选择")
            
            return "日志查看完成"
            
        except Exception as e:
            self.handle_error(e, "日志查看")
            return None
    
    def _show_recent_logs(self, available_logs):
        """显示最新日志"""
        if len(available_logs) == 1:
            log_file = available_logs[0]['path']
        else:
            print("\n选择要查看的日志文件:")
            for i, log in enumerate(available_logs, 1):
                print(f"   {i}. {log['name']}")
            
            choice = input(f"请选择 (1-{len(available_logs)}): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available_logs):
                    log_file = available_logs[idx]['path']
                else:
                    print("❌ 无效选择")
                    return
            except ValueError:
                print("❌ 请输入有效数字")
                return
        
        try:
            print(f"\n📄 {log_file.name} - 最新50行:")
            print("="*50)
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-50:] if len(lines) > 50 else lines
                
                for line in recent_lines:
                    # 简单的颜色标记
                    line = line.rstrip()
                    if 'ERROR' in line:
                        print(f"❌ {line}")
                    elif 'WARNING' in line:
                        print(f"⚠️ {line}")
                    elif 'INFO' in line:
                        print(f"ℹ️ {line}")
                    else:
                        print(f"   {line}")
            
            print("="*50)
            input("按Enter继续...")
            
        except Exception as e:
            print(f"❌ 读取日志失败: {e}")
    
    def _search_logs(self, available_logs):
        """搜索日志内容"""
        search_term = input("\n🔍 请输入搜索关键词: ").strip()
        if not search_term:
            return
        
        print(f"\n搜索结果 (关键词: '{search_term}'):")
        print("="*50)
        
        total_matches = 0
        for log in available_logs:
            try:
                with open(log['path'], 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                matches = []
                for i, line in enumerate(lines, 1):
                        if search_term.lower() in line.lower():
                            matches.append((i, line.rstrip()))
                    
                if matches:
                    print(f"\n📄 {log['name']} ({len(matches)} 条匹配):")
                    for line_num, line in matches[-10:]:  # 显示最新10条
                        print(f"   {line_num:4d}: {line}")
                    total_matches += len(matches)
                    
            except Exception as e:
                print(f"❌ 搜索 {log['name']} 时出错: {e}")
        
        print(f"\n总共找到 {total_matches} 条匹配记录")
        input("按Enter继续...")
    
    def _show_log_stats(self, available_logs):
        """显示日志统计"""
        print("\n📊 日志统计信息:")
        print("="*40)
        
        for log in available_logs:
            try:
                with open(log['path'], 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 统计不同级别的日志
                info_count = sum(1 for line in lines if 'INFO' in line)
                warn_count = sum(1 for line in lines if 'WARNING' in line)
                error_count = sum(1 for line in lines if 'ERROR' in line)
                
                print(f"\n📄 {log['name']}:")
                print(f"   总行数: {len(lines)}")
                print(f"   ℹ️ INFO: {info_count}")
                print(f"   ⚠️ WARNING: {warn_count}")
                print(f"   ❌ ERROR: {error_count}")
                print(f"   文件大小: {log['size']:.2f}MB")
                
            except Exception as e:
                print(f"❌ 分析 {log['name']} 时出错: {e}")
        
        input("按Enter继续...")
    
    def _cleanup_logs(self, available_logs):
        """清理旧日志"""
        print("\n🧹 日志清理选项:")
        print("1. 清空所有日志文件 (保留文件)")
        print("2. 删除7天前的日志行")
        print("3. 压缩大型日志文件")
        print("0. 取消")
        
        choice = input("\n请选择 (0-3): ").strip()
        
        if choice == "1":
            if input("⚠️ 确认清空所有日志？(y/N): ").lower() == 'y':
                for log in available_logs:
                    try:
                        with open(log['path'], 'w', encoding='utf-8') as f:
                            f.write(f"# 日志已于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 清空\n")
                        print(f"✅ 已清空 {log['name']}")
                    except Exception as e:
                        print(f"❌ 清空 {log['name']} 失败: {e}")
        elif choice == "2":
            print("💡 按日期清理功能需要更复杂的日志解析，当前版本暂不支持")
        elif choice == "3":
            print("💡 日志压缩功能将在未来版本中实现")
        
        if choice != "0":
            input("按Enter继续...")
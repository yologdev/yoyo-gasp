import os, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCANNER=str(ROOT/'.agent/bin/gitleaks')
class CredentialGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.repo=Path(self.tmp.name)
        subprocess.run(['git','init','-q',str(self.repo)],check=True)
    def tearDown(self):self.tmp.cleanup()
    def stage(self,path,text):
        p=self.repo/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
        subprocess.run(['git','-C',str(self.repo),'add','--',path],check=True)
    def scan(self,**extra):
        env={**os.environ,'GITLEAKS_BIN':SCANNER,**extra}
        return subprocess.run(['python3',str(ROOT/'scripts/check-secrets.py'),'--repo',str(self.repo)],env=env,capture_output=True,text=True)
    def test_clean(self):
        self.stage('memory/facts.jsonl','{"text":"Read chapter twelve."}');self.assertEqual(self.scan().returncode,0)
    def test_session_path(self):
        self.stage('.yoyo/last-session.json','[]');self.assertEqual(self.scan().returncode,1)
    def test_staged_bytes_not_worktree(self):
        value='ghp_'+'Ab3Cd4Ef5Gh6Ij7Kl8Mn9Op0Qr1St2Uv3Wx4'
        self.stage('notes.md','token = '+value);(self.repo/'notes.md').write_text('clean')
        result=self.scan();self.assertEqual(result.returncode,1);self.assertNotIn(value,result.stdout+result.stderr)
    def test_exact_opaque_runtime_credential(self):
        value='opaque-'+''.join(chr(65+i) for i in range(20))
        self.stage('notes.md','unlabelled '+value)
        result=self.scan(TEST_API_KEY=value);self.assertEqual(result.returncode,1);self.assertNotIn(value,result.stdout+result.stderr)
    def test_missing_scanner_blocks(self):
        self.stage('notes.md','clean');self.assertEqual(self.scan(GITLEAKS_BIN='/missing/gitleaks').returncode,2)
if __name__=='__main__':unittest.main()

"""No-network synthetic Git history tests of the dormant H1 first-add ancestry rule."""
import subprocess
import tempfile
from pathlib import Path
import unittest

LAUNCH='docs/astra/GUITARTECHS_H1_20EPOCH_PAIRED_PILOT_TRAINING_LAUNCH_V1.json'


def git(root, *args):
    return subprocess.check_output(['git','-C',str(root),*args],text=True,stderr=subprocess.DEVNULL).strip()


def first_add_eligible(root):
    history=git(root,'rev-list','--count','HEAD','--',LAUNCH)
    changed=git(root,'diff-tree','--no-commit-id','--name-status','-r','--root','HEAD','--',LAUNCH)
    return history=='1' and changed=='A\t'+LAUNCH


class SyntheticGitAncestry(unittest.TestCase):
    def setup_repo(self, root):
        git(root,'init','-q')
        git(root,'config','user.name','Synthetic Only')
        git(root,'config','user.email','offline@example.invalid')
        (root/'README').write_text('synthetic only\n')
        git(root,'add','README')
        git(root,'commit','-qm','initial')

    def commit_file(self, root, text):
        path=root/LAUNCH
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(text)
        git(root,'add',LAUNCH)
        git(root,'commit','-qm','synthetic receipt')

    def test_exact_first_introduction_only(self):
        with tempfile.TemporaryDirectory() as path:
            root=Path(path)
            self.setup_repo(root)
            self.assertFalse(first_add_eligible(root))
            self.commit_file(root,'synthetic\n')
            self.assertTrue(first_add_eligible(root))

    def test_edit_is_not_single_use(self):
        with tempfile.TemporaryDirectory() as path:
            root=Path(path)
            self.setup_repo(root)
            self.commit_file(root,'synthetic\n')
            self.commit_file(root,'synthetic edit\n')
            self.assertFalse(first_add_eligible(root))
            self.assertEqual(git(root,'rev-list','--count','HEAD','--',LAUNCH),'2')

    def test_delete_and_readd_is_rejected(self):
        with tempfile.TemporaryDirectory() as path:
            root=Path(path)
            self.setup_repo(root)
            self.commit_file(root,'synthetic\n')
            (root/LAUNCH).unlink()
            git(root,'add','-u')
            git(root,'commit','-qm','synthetic deletion')
            self.commit_file(root,'readded synthetic\n')
            self.assertFalse(first_add_eligible(root))


if __name__=='__main__': unittest.main()

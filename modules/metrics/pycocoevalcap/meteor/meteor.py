
import os
import subprocess
import threading


METEOR_JAR = "meteor-1.5.jar"


class Meteor:

    def __init__(self):
        jar_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            METEOR_JAR
        )

        if not os.path.exists(jar_path):
            raise FileNotFoundError(
                f"METEOR JAR not found: {jar_path}"
            )

        self.meteor_cmd = [
            "java",
            "-XX:+PerfDisableSharedMem",
            "-Xmx2G",
            "-jar",
            jar_path,
            "-", "-", "-stdio", "-l", "en", "-norm"
        ]

        self.meteor_p = subprocess.Popen(
            self.meteor_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1
        )

        self.lock = threading.Lock()
        self._closed = False

    def compute_score(self, gts, res):
        assert gts.keys() == res.keys()

        imgIds = list(gts.keys())
        scores = []

        eval_line = "EVAL"

        with self.lock:
            for i in imgIds:
                assert len(res[i]) == 1

                stat = self._stat(res[i][0], gts[i])
                eval_line += " ||| {}".format(stat)

            self.meteor_p.stdin.write(eval_line + "\n")
            self.meteor_p.stdin.flush()

            for _ in imgIds:
                scores.append(float(self.meteor_p.stdout.readline().strip()))

            score = float(self.meteor_p.stdout.readline().strip())

        return score, scores

    def _stat(self, hypothesis_str, reference_list):
        hypothesis_str = hypothesis_str.replace("|||", "")
        hypothesis_str = hypothesis_str.replace("  ", " ")

        score_line = " ||| ".join(
            ("SCORE", " ||| ".join(reference_list), hypothesis_str)
        )

        score_line = score_line.replace("\n", "").replace("\r", "")

        self.meteor_p.stdin.write(score_line + "\n")
        self.meteor_p.stdin.flush()

        return self.meteor_p.stdout.readline().strip()

    def method(self):
        return "METEOR"

    def close(self):
        if self._closed:
            return

        self._closed = True

        if self.meteor_p.poll() is None:
            try:
                self.meteor_p.stdin.close()
                self.meteor_p.wait(timeout=3)
            except (subprocess.TimeoutExpired, OSError):
                self.meteor_p.kill()
                self.meteor_p.wait()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

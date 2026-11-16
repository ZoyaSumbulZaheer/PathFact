from modules.metrics.pycocoevalcap.meteor.meteor import Meteor

print("Starting METEOR test...", flush=True)

meteor = Meteor()

print("METEOR Java process started.", flush=True)

try:
    gts = {0: ["a cat sits on the mat"]}
    res = {0: ["a cat is sitting on the mat"]}

    score, scores = meteor.compute_score(gts, res)

    print("METEOR test successful!", flush=True)
    print("Score:", score)
    print("Individual scores:", scores)

finally:
    meteor.close()
import unittest

from gh_hotspot_analyzer.analyzer import analyze_payload, compute_score


def sample_repo(**overrides):
    repo = {
        "full_name": "demo/repo",
        "html_url": "https://github.com/demo/repo",
        "description": "sample",
        "language": "Python",
        "stargazers_count": 100,
        "forks_count": 20,
        "watchers_count": 30,
        "open_issues_count": 5,
        "created_at": "2026-03-01T00:00:00Z",
        "updated_at": "2026-03-20T00:00:00Z",
        "topics": ["ai", "analytics"],
    }
    repo.update(overrides)
    return repo


class AnalyzerTests(unittest.TestCase):
    def test_compute_score_prefers_more_popular_and_active_repo(self):
        higher = sample_repo(stargazers_count=200, updated_at="2026-03-23T00:00:00Z")
        lower = sample_repo(stargazers_count=50, updated_at="2026-03-10T00:00:00Z")
        self.assertGreater(compute_score(higher), compute_score(lower))

    def test_analyze_payload_builds_summary(self):
        payload = {"items": [sample_repo(), sample_repo(full_name="demo/repo2", language="Go", topics=["cli"])]}
        analysis = analyze_payload(payload)
        self.assertEqual(analysis["summary"]["total_repositories"], 2)
        self.assertIn("Python", analysis["language_distribution"])
        self.assertGreaterEqual(analysis["top_repositories"][0]["score"], analysis["top_repositories"][1]["score"])

if __name__ == "__main__":
    unittest.main()


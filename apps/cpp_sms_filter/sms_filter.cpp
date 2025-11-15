#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <algorithm>

struct Pattern {
    std::string word;
    std::string category; // "bank", "otp", "link", "offer"
    int weight;
};

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: sms_filter <sms.txt> [--stats]\n";
        return 1;
    }
    bool stats = (argc >= 3 && std::string(argv[2]) == "--stats");

    std::vector<Pattern> patterns = {
        {"KYC", "bank", 3}, {"kyc", "bank", 3},
        {"account blocked", "bank", 3},
        {"verify", "bank", 2},
        {"UPI", "bank", 3}, {"upi", "bank", 3},
        {"Aadhaar", "bank", 3}, {"aadhaar", "bank", 3},
        {"PAN", "bank", 3}, {"pan", "bank", 3},
        {"OTP", "otp", 3}, {"otp", "otp", 3},
        {"reset", "otp", 2},
        {"refund", "offer", 2},
        {"90% off", "offer", 2},
        {"prize", "offer", 2},
        {"gift", "offer", 1},
        {"bit.ly", "link", 3},
        {"tinyurl", "link", 3},
        {".cn", "link", 2},
        {".ru", "link", 2}
    };

    std::ifstream in(argv[1]);
    if (!in) {
        std::cerr << "Cannot open " << argv[1] << "\n";
        return 1;
    }

    std::string line;
    int total = 0, flagged = 0;
    std::map<std::string,int> categoryCounts;

    while (std::getline(in, line)) {
        if (line.empty()) continue;
        ++total;

        std::string L = line;
        std::transform(L.begin(), L.end(), L.begin(), ::tolower);

        int score = 0;
        std::set<std::string> hitCategories;

        for (auto &p : patterns) {
            std::string patLower = p.word;
            std::transform(patLower.begin(), patLower.end(), patLower.begin(), ::tolower);
            if (L.find(patLower) != std::string::npos) {
                score += p.weight;
                hitCategories.insert(p.category);
                categoryCounts[p.category]++;
            }
        }

        if (score > 0) {
            ++flagged;
            std::string severity;
            if (score >= 5) severity = "HIGH";
            else if (score >= 3) severity = "MEDIUM";
            else severity = "LOW";

            std::cout << "[SUSPECT:" << severity << "] " << line << "\n";
        }
    }

    std::cout << "Scanned " << total << " messages, flagged " << flagged << "\n";
    if (stats) {
        std::cout << "Category stats:\n";
        for (auto &kv : categoryCounts) {
            std::cout << "  " << kv.first << ": " << kv.second << "\n";
        }
    }
    return 0;
}

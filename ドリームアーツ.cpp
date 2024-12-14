#include <bits/stdc++.h>
using namespace std;

using T = tuple<int, int, double>;

int main() {
    vector<T> keiro;
    cout << "データを入力してください" << endl;

    string line;
    while (getline(cin, line)) {
        istringstream nyuuryoku(line);
        int start, end;
        double distance;
        char comma1, comma2;
        if (nyuuryoku >> start >> comma1 >> end >> comma2 >> distance && comma1 == ',' && comma2 == ',') {
            keiro.push_back(T(start, end, distance));
        } else {
            cout << "フォーマットが正しくありません: " << line << endl;
        }
    }

    map<int, vector<pair<int, double>>> rosen;
    for (auto& [start, end, distance] : keiro) {
        rosen[start].push_back({end, distance});
    }

    double maxDistance = -1;
    vector<int> maxPath;
    vector<int> currentPath;
    set<int> visited;

    function<void(int, double)> dfs = [&](int current, double currentDistance) {
        currentPath.push_back(current);
        visited.insert(current);

        if (currentPath.size() > 1 && currentDistance > maxDistance) {
            maxDistance = currentDistance;
            maxPath = currentPath;
        }

        for (auto& [next, dist] : rosen[current]) {
            if (visited.count(next) == 0) {
                dfs(next, currentDistance + dist);
            }
        }

        visited.erase(current);
        currentPath.pop_back();
    };

    bool hasValidRoute = false;
    for (auto& [start, _] : rosen) {
        dfs(start, 0);
        if (!maxPath.empty()) {
            hasValidRoute = true;
        }
    }

    if (maxPath.empty()) {
        double maxDistanceNoRoute = -1;
        pair<int, int> maxRoutePair;
        
        for (auto& [start, _] : rosen) {
            for (auto& [end, distance] : rosen[start]) {
                if (distance > maxDistanceNoRoute) {
                    maxDistanceNoRoute = distance;
                    maxRoutePair = {start, end};
                }
            }
        }

        cout << "最大距離の経路" << endl;
        cout << "経路: " << maxRoutePair.first << " -> " << maxRoutePair.second << endl;
        cout << "距離の合計: " << maxDistanceNoRoute << endl;
    } else {
        cout << "最大距離の経路:" << endl;
        cout << "経路: ";
        for (int node : maxPath) {
            cout << node << " ";
        }
        cout << endl;
        cout << "距離の合計: " << maxDistance << endl;
    }

    return 0;
}

#include <nlohmann/json.hpp>
#include <iostream>

int main(int argc, char **argv) {

    // Create a JSON object
    nlohmann::json j;
    j["name"] = "John";
    j["age"] = 30;

    // Print the JSON object
    std::cout << j.dump(4) << std::endl;

    return 0;
}

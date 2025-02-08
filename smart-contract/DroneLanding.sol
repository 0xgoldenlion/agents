// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract DroneLanding {
    address public owner;

    struct LandingRequest {
        address drone;
        bool approved;
        string landingZone;
    }

    mapping(address => LandingRequest) public requests;

    event LandingRequested(address drone);
    event LandingApproved(address drone, string landingZone);
    event LandingRequestsReset();

    constructor() {
        owner = msg.sender;
    }

    function requestLanding() external {
        require(requests[msg.sender].drone == address(0), "Landing request already exists");

        requests[msg.sender] = LandingRequest({
            drone: msg.sender,
            approved: false,
            landingZone: ""
        });

        emit LandingRequested(msg.sender);
    }

    function autoApproveLanding(address drone) external {
        require(requests[drone].drone != address(0), "No request found");

        // Auto-approve with external script
        requests[drone].approved = true;
        requests[drone].landingZone = "Zone A"; // Default landing zone

        emit LandingApproved(drone, "Zone A");
    }

    function getLandingStatus(address drone) external view returns (bool, string memory) {
        require(requests[drone].drone != address(0), "No request found");
        return (requests[drone].approved, requests[drone].landingZone);
    }

    function resetLandingRequests() external {
        require(msg.sender == owner, "Only owner can reset landing requests");

        // Reset all drone requests
        for (uint256 i = 0; i < 256; i++) {
            if (requests[address(uint160(i))].drone != address(0)) {
                delete requests[address(uint160(i))];
            }
        }

        emit LandingRequestsReset();
    }
}

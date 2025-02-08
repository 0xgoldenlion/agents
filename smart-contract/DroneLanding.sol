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
    address[] public requestList; // Stores all addresses with requests

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

        requestList.push(msg.sender); // Track the new request

        emit LandingRequested(msg.sender);
    }

    function autoApproveLanding(address drone) external {
        require(requests[drone].drone != address(0), "No request found");

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

        // Iterate over all stored drone addresses and delete requests
        for (uint256 i = 0; i < requestList.length; i++) {
            delete requests[requestList[i]];
        }

        // Reset the request list
        delete requestList;

        emit LandingRequestsReset();
    }

     function getAllRequests() external view returns (LandingRequest[] memory) {
        LandingRequest[] memory allRequests = new LandingRequest[](requestList.length);

        for (uint256 i = 0; i < requestList.length; i++) {
            allRequests[i] = requests[requestList[i]];
        }

        return allRequests;
    }
}

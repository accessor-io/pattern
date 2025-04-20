// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../contracts/EVMPuzzle.sol";

contract EVMPuzzleTest is Test {
    EVMPuzzle public puzzle;
    
    function setUp() public {
        puzzle = new EVMPuzzle();
    }
    
    function testInitialState() public {
        (uint256 layer, bytes32 state) = puzzle.getPuzzleState();
        assertEq(layer, 0, "Initial layer should be 0");
        assertTrue(state != bytes32(0), "Initial state should not be zero");
        assertFalse(puzzle.isSolved(), "Puzzle should not be solved initially");
    }
    
    function testInvalidSolution() public {
        bool success = puzzle.submitSolution(bytes32(0));
        assertFalse(success, "Zero solution should not work");
        
        (uint256 layer, ) = puzzle.getPuzzleState();
        assertEq(layer, 0, "Layer should not advance on invalid solution");
    }
    
    function testSolvedPuzzleReject() public {
        // Force puzzle into solved state
        vm.store(
            address(puzzle),
            bytes32(uint256(2)), // puzzleSolved storage slot
            bytes32(uint256(1))  // true
        );
        
        vm.expectRevert("Puzzle already solved");
        puzzle.submitSolution(bytes32(0));
    }
    
    function testLayerProgression() public {
        // This test demonstrates how layers should progress
        // Note: Actual solutions are not provided as they are part of the puzzle
        (uint256 initialLayer, ) = puzzle.getPuzzleState();
        assertEq(initialLayer, 0, "Should start at layer 0");
        
        // Try an invalid solution
        bool success = puzzle.submitSolution(bytes32(uint256(1)));
        assertFalse(success, "Random solution should not work");
        
        (uint256 currentLayer, ) = puzzle.getPuzzleState();
        assertEq(currentLayer, initialLayer, "Layer should not advance on invalid solution");
    }
    
    function testEmitEvents() public {
        // Set up event monitoring
        vm.expectEmit(true, true, false, true);
        emit EVMPuzzle.LayerCompleted(0, address(this));
        
        // Note: This will fail as we don't provide actual solution
        puzzle.submitSolution(bytes32(0));
    }
    
    // Helper function to verify storage layout
    function testStorageLayout() public {
        bytes32 slot0 = vm.load(address(puzzle), bytes32(uint256(0))); // layerStates
        bytes32 slot1 = vm.load(address(puzzle), bytes32(uint256(1))); // currentLayer
        bytes32 slot2 = vm.load(address(puzzle), bytes32(uint256(2))); // puzzleSolved
        
        assertTrue(slot0 != bytes32(0), "Initial state should be set");
        assertEq(uint256(slot1), 0, "Initial layer should be 0");
        assertEq(uint256(slot2), 0, "Should not be solved initially");
    }
} 
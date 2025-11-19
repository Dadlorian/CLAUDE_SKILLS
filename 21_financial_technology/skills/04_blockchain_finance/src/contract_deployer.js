/**
 * Contract Deployer - Deploy and manage smart contracts
 */

const { ethers } = require('hardhat');
const fs = require('fs');

class ContractDeployer {
  constructor(signer) {
    this.signer = signer;
    this.deployments = {};
  }

  /**
   * Deploy contract
   */
  async deployContract(contractName, args = []) {
    console.log(`Deploying ${contractName}...`);

    const Contract = await ethers.getContractFactory(contractName);
    const contract = await Contract.connect(this.signer).deploy(...args);
    await contract.deployed();

    console.log(`${contractName} deployed to: ${contract.address}`);

    this.deployments[contractName] = {
      address: contract.address,
      args,
      network: (await ethers.provider.getNetwork()).name,
      blockNumber: await ethers.provider.getBlockNumber()
    };

    return contract;
  }

  /**
   * Verify contract on Etherscan
   */
  async verifyContract(contractName, address, args = []) {
    try {
      await ethers.provider.send('hardhat_mine', ['0x1000']);
      console.log(`Verifying ${contractName} on Etherscan...`);

      await hre.run('verify:verify', {
        address,
        constructorArguments: args
      });

      console.log('Verification successful');
    } catch (error) {
      console.error('Verification failed:', error);
    }
  }

  /**
   * Save deployment info
   */
  saveDeployments(filename = 'deployments.json') {
    fs.writeFileSync(
      filename,
      JSON.stringify(this.deployments, null, 2)
    );
  }

  /**
   * Load deployment info
   */
  loadDeployments(filename = 'deployments.json') {
    if (fs.existsSync(filename)) {
      const data = fs.readFileSync(filename, 'utf8');
      this.deployments = JSON.parse(data);
    }
  }
}

module.exports = ContractDeployer;

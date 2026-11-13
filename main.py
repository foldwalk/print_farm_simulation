from argparse import ArgumentParser

from simulation import Simulation

if __name__ == "__main__":
    # parse config file
    parser = ArgumentParser()
    parser.add_argument(
        'business_config',
        default="toy_shop",
        nargs="?",
        help="The business config file location",
    )
    parser.add_argument(
        'space_config',
        default="single_desk",
        nargs="?",
        help="The space config file location",
    )
    
    args = parser.parse_args()
    
    sim = Simulation(args.business_config, args.space_config)
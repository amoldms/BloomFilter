import sys
import mmh3
from math import log, ceil
from bitarray import bitarray
import middletier.logger as logger
from bloom_filter.bloomfilter_interface import BloomFilterInterface


class BloomFilter(BloomFilterInterface):
    """
    A Bloom Filter class, probabilistic data structure. A Bloom filter offers an approximate containment test
    with one-sided error. It tells us that the element either definitely is not in the set or probably is in the set.
    Useful for scenarios where fraction of false positives are acceptable, however false negative are not.

    ...

    Attributes
    ----------
    probability : float
        The expected false positive probability for bloom filter
    items_count : int
        The number of items expected to be stored in bloom filter
    filter_size : int
        The bit array size of bloom filter
    hash_count : int
        The number of hash functions used to hash item
    case_sensitive : bool
        Flag indicating if items in bloom filter are case sensitive

    Methods
    -------
    add(self, items)
        Adds new items to bloom filter
    contain(self, item)
        Checks existence of item. Returns True if item probably exists in bloom filter, False if item doesn't exist
    get_hash(cls, item)
        Returns two hash values using single hash function on item
    get_filter_size(cls, items_count, probability)
        Returns bloom filter bit array size based on items_count and probability
    get_hash_count(cls, items_count, filter_size)
        Returns count of hash functions to be used based on items_count and filter_size
    """

    def __init__(self, items, probability, case=False):
        """
        Parameters
        ----------
        items : int
            The number of items expected to be stored in bloom filter
        probability : float
            The bloom filter's expected false positive probability
        """

        self.items_count = items
        self.probability = probability
        self.case_sensitive = case
        self.counter = 0
        self.delete_threshold = False

        # Set size of filter bit array
        self.filter_size = self.get_filter_size(items, probability)

        # Set count of hash functions
        self.hash_count = self.get_hash_count(items, self.filter_size)

        # Create bit array and initialize all bits to 0
        self.bloom_bitarray = bitarray(self.filter_size)
        self.bloom_bitarray.setall(0)

    def add(self, item):
        """ Adds items to bloom filter by setting bit to 1 for every position generated by each hash function.
        ...
        Parameters
        ----------
        item : item to be added
            The item to be added in bloom filter
        """
        # Get hash values tuple from get_hash function
        # To improve performance avoid multiple hash computes. Compute hash only once and use it in linear equations.
        hash_val1, hash_val2 = self.get_hash(str(item), self.case_sensitive)

        # Use above hash values in linear family of equation to simulate multiple hash functions.
        # Performance is significantly improved by skipping need to compute hash for every hash function iteration.
        # Add item by setting bit to 1 for every position generated by each hash function.
        try:
            current_hash = hash_val1
            for i in range(self.hash_count):
                position = current_hash % self.filter_size
                self.bloom_bitarray[position] = 1
                current_hash += hash_val2
            self.counter += 1
        except Exception as e:
            # ToDo: Implement granular exception handling
            logger.log(str(e))
            sys.exit(1)

    def bulk_add(self, items):
        """ Adds items to bloom filter in bulk by setting bit to 1 for every position generated by each hash function.
        ...
        Parameters
        ----------
        items : list of items to be added
            The item to be added in bloom filter
        """
        # Get hash values tuple from get_hash function
        # To improve performance avoid multiple hash computes. Compute hash only once and use it in linear equations.
        # ToDo: Parallelize this method using map-reduce for initial bulk load as well as replica creation
        try:
            for item in items:
                self.add(item)
        except Exception as e:
            logger.log(str(e))
            sys.exit(1)

    def contain(self, item):
        """ Checks existence of item. Returns True if item probably exists in bloom filter, False if item doesn't exist
        ...
        Parameters
        ----------
        item : object
            The item to be checked for existence

        Returns
        -------
        bool
            True if item probably exists in filter, False if item doesn't exist
        """
        # Get hash values tuple from get_hash function
        # To improve performance avoid multiple hash computes. Compute hash only once and use it in linear equations.
        hash_val1, hash_val2 = self.get_hash(item, self.case_sensitive)

        # Use above hash values in linear family of equation to simulate multiple hash functions.
        # Check probable existence of item by checking that none hash value bits for that item being zero
        try:
            current_hash = hash_val1
            for i in range(self.hash_count):
                position = current_hash % self.filter_size
                if not self.bloom_bitarray[position]:
                    return False
                current_hash += hash_val2
            return True
        except Exception as e:
            logger.log(str(e))
            sys.exit(1)

    @classmethod
    def get_hash(cls, item, case_sensitive):
        """ Returns two hash values computed using single hash function on item
        ...
        Parameters
        ----------
        item : object
            The input element to add or check
        case_sensitive: bool
            Flag indicates if item value is case sensitive

        Returns
        -------
        tuple
            Two hash values computing using mmh3 hash function
        """
        try:
            # If case sensitive is False, convert item to lowercase for add and exist methods, to enable case difference
            if case_sensitive:
                item = item.lower()

            # Hashing is compute intensive. Hence we compute it only once.
            # Using non-cryptographic hash function is highly performance efficient and serves purpose of bloom filter.
            # mmh3.hash64 hash function returns two hash values for input item
            hash_vals = mmh3.hash64(item)
            return hash_vals
        except Exception as e:
            logger.log(str(e))
            sys.exit(1)

    @classmethod
    def get_filter_size(cls, items, prob):
        """ Returns bloom filter bit array size based on items_count and probability
        ...
        Parameters
        ----------
        items : int
            The number of items expected to be stored in bloom filter
        prob : float
            The bloom filter's expected false positive probability

        Returns
        -------
        int
            bit array size
        """
        # Calculate size of bit array using standard formula = (ceil((items * log(prob)) / log(1 / pow(2, log(2)))))
        try:
            size = ceil((items * log(prob)) / log(1 / pow(2, log(2))))
            return size
        except Exception as e:
            # ToDo: Implement granular exception handling
            logger.log(str(e))
            sys.exit(1)

    @classmethod
    def get_hash_count(cls, items, size):
        """ Returns number of hash functions needed based on items_count and filter bit array size
        ...
        Parameters
        ----------
        items : int
            The number of items expected to be stored in bloom filter
        size : int
            The Size of bit array

        Returns
        -------
        int
            The count of hash functions
        """
        # Calculate count of hash functions needed using standard formula = (round((size / items) * log(2)))
        try:
            count = round((size / items) * log(2))
            return count
        except Exception as e:
            # ToDo: Implement granular exception handling
            logger.log(str(e))
            sys.exit(1)

# ToDo: Granular exception handling implementation for null check, data type mismatch, value error, IO Error,
#       user input error, arithmetic operations  etc.

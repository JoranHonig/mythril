contract MyContract {

  function foo(uint256 a) returns(uint256) {
    if(a >= 0){ //this will never be false
      return 0;
    }
    return 1;
  }
}

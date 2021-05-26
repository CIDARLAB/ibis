module sr_latch(output q, p, input s, r);

   nor(q, r, p);
   nor(p, q, s);

endmodule

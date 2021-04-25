/* 
 or gate
*/
module or_gate
(
 a,
 b,
 out
 );

   input a;
   input b;

   output out;

   assign out = a | b;
 
endmodule // or_gate
